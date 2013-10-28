import os
import boto
import sys
import logging
import time
import string
import random
from boto.ec2.connection import EC2Connection
from boto.ec2.autoscale import AutoScaleConnection
from boto.ec2.autoscale import LaunchConfiguration
from boto.ec2.autoscale import AutoScalingGroup
from boto.ec2.autoscale import ScalingPolicy
from boto.ec2.autoscale import Tag
from boto.ec2.cloudwatch import MetricAlarm
from boto.ec2.blockdevicemapping import BlockDeviceType
from boto.ec2.blockdevicemapping import BlockDeviceMapping

#logging.basicConfig(filename='/tmp/setupAS.log',filemode='w',level=logging.DEBUG)
# Get values from cmd line
ELB_NAME        = sys.argv[1]
REGION          = sys.argv[2]
INSTANCE        = sys.argv[3]
KEY             = sys.argv[4]
SECGRP          = sys.argv[5]
TYPE            = sys.argv[6]
AZLIST          = sys.argv[7]
VPC_ZONE        = sys.argv[8]
ROLE            = sys.argv[9]

#generate random string to append to launch config and AS group names to prevent collisions
randomStr = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))
asLCstr = 'AlfrescoLC-' + randomStr
asGrpStr = 'AlfrescoGrp-'+ randomStr 
#connect to region
logging.debug(  ' region %s  ELB %s   INSTANCE %s  KEY %s  SECGRP %s TYPE %s  AZLIST %s  VPC_ZONE %s ROLE %s', REGION, ELB_NAME, INSTANCE, KEY, SECGRP, TYPE, AZLIST, VPC_ZONE, ROLE)
conn = boto.ec2.connect_to_region(REGION)
conn_as = boto.ec2.autoscale.connect_to_region(REGION)

#create new image from this running instance
AMIID = conn.create_image(INSTANCE, 'AlfrescoClusterAMI-'+ randomStr, 'Alfreco Cluster AMI for Autoscaling Group', True)
logging.debug( ' AMIID=%s', AMIID)
time.sleep(20)

#setup ephemeral0 for local cache
blockDeviceMap = boto.ec2.blockdevicemapping.BlockDeviceType()
blockDeviceMap.ephemeral_name = 'ephemeral0'
bdm = BlockDeviceMapping()
bdm['/dev/sdh'] = blockDeviceMap
#create user-data string
userData = '#!/bin/bash \n cur=$(hostname  | sed \'s/-/./g\' | cut -c4-18) \n echo \"alfresco.jgroups.bind_address=$cur\"   >> /opt/alfresco/tomcat/shared/classes/alfresco-global.properties \n echo \"alfresco.ehcache.rmi.hostname=$cur\"  >> /opt/alfresco/tomcat/shared/classes/alfresco-global.properties \n cur1=$(hostname)\n echo \"$cur $cur1\" >> /etc/hosts\n'
#create launch configuration and AS group
launchConfig = LaunchConfiguration(name=asLCstr, image_id=AMIID, key_name=KEY, security_groups=[SECGRP], instance_type=TYPE, instance_monitoring=True, instance_profile_name=ROLE, block_device_mappings=[bdm], user_data=userData)
conn_as.create_launch_configuration(launchConfig)
time.sleep(20)
autoscaleGroup = AutoScalingGroup(group_name=asGrpStr , load_balancers=[ELB_NAME], availabilty_zones=[AZLIST], launch_config=launchConfig, vpc_zone_identifier=VPC_ZONE, min_size=2, max_size=6, health_check_period='360', health_check_type='ELB')
conn_as.create_auto_scaling_group(autoscaleGroup)

#setup tagging for the instances

# create a Tag for the austoscale group
as_tag = Tag(key='Name', value = 'Alfresco Server', propagate_at_launch=True, resource_id=asGrpStr)

# Add the tag to the autoscale group
conn_as.create_or_update_tags([as_tag])

#create scale up and scale down policies for the autoscale group
scaleUpPolicy = ScalingPolicy(name='alfrescoScaleUp-'+randomStr, adjustment_type='ChangeInCapacity', as_name=autoscaleGroup.name, scaling_adjustment=2, cooldown=400)
scaleDownPolicy = ScalingPolicy(name='alfrescoScaleDown-'+randomStr, adjustment_type='ChangeInCapacity', as_name=autoscaleGroup.name, scaling_adjustment=-1, cooldown=400) 
conn_as.create_scaling_policy(scaleUpPolicy)
conn_as.create_scaling_policy(scaleDownPolicy)

#redeclare policies to populate the ARN fields 
policyResults = conn_as.get_all_policies(as_group=autoscaleGroup.name, policy_names=[scaleUpPolicy.name])
scaleUpPolicy = policyResults[0]

policyResults = conn_as.get_all_policies(as_group=autoscaleGroup.name, policy_names=[scaleDownPolicy.name])
scaleDownPolicy = policyResults[0]

#connect to Cloud Watch
cw_conn = boto.ec2.cloudwatch.connect_to_region(REGION)

#create the following alarms: ScaleUp @ Avg CPU >60% over 2 periods OR ELB latency >= 0.5sec.  ScaleDown @ Avg CPU <30% over 2 periods

dimensions = {"AutoScalingGroupName" : autoscaleGroup.name}
dimensions_elb = {"LoadBalancerName" : ELB_NAME} 
scaleUpAlarmCPU = MetricAlarm(name='Alfresco-HighCPU', namespace='AWS/EC2',metric='CPUUtilization', statistic='Average', comparison='>', threshold='60', evaluation_periods=2, period=60, unit='Percent' , alarm_actions=[scaleUpPolicy.policy_arn], dimensions=dimensions)

scaleDownAlarmCPU = MetricAlarm(name='Alfresco-LowCPU', namespace='AWS/EC2',metric='CPUUtilization', statistic='Average', comparison='<', threshold='30', evaluation_periods=2, period=60, unit='Percent', alarm_actions=[scaleDownPolicy.policy_arn], dimensions=dimensions)

scaleUpAlarmLatency = MetricAlarm(name='Alfresco-HighLatency', namespace='AWS/ELB', metric='Latency', statistic='Average', comparison='>', threshold='1', evaluation_periods=2, period=60, unit='Seconds', alarm_actions=[scaleUpPolicy.policy_arn],dimensions=dimensions_elb)

cw_conn.create_alarm(scaleUpAlarmCPU)
cw_conn.create_alarm(scaleDownAlarmCPU)
cw_conn.create_alarm(scaleUpAlarmLatency)
 
## TODO: uncomment terminate instance command 
#Terminate this setup instance now that auto-scaling is configured
conn.terminate_instances(INSTANCE)

#done

