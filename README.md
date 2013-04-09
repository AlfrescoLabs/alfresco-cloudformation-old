Alfresco CloudFormation Template
================================

Overview
--------

This template will instantiate a 2-node Alfresco cluster with the following capabilities:
* All Alfresco nodes will be placed inside a Virtual Private Cloud (VPC).
* An Elastic Load Balancer instance with "sticky" sessions based on the Tomcat JSESSIONID.
* Shared S3 ContentStore
* MySQL database on RDS instances.
* Each Alfresco node will be in a separate Availability Zone.
* Auto-scaling roles that will add extra Alfresco nodes when certain performance thresholds are reached.

Basic Usage
-----------

* Launch the [AWS Console](http://aws.amazon.com/console/cloudformation)
* Click *Create Stack*.
* Name and upload the Alfresco CloudFormation Template.
* Click *Continue*.
* Fill out the form making sure you review the following:
	* Ensure you use the name of an existing S3 bucket.
	* Verify the instance sizes and be mindful of the hourly costs.
	* Provide the logins and passwords for the database and Alfresco admin accounts. These accounts and passwords will be created & set by the template.
	* Ensure you set the correct EC2 key.
* Click *Continue* and finish the wizard.

Tips
----
* The instances will take 10-15 minutes to start.
* Use the *Events* tab to review status and any errors.
* Once the environment starts, use the *Output* tab to get the URL of the load-balancer.
* If stack deletion does not complete and the *Events* show an error related to VPC, login to the VPC console and delete the corresponding VPC; then delete the stack again.