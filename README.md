Alfresco CloudFormation Template
================================

*WATCH OUT!* A new version of this template for Alfresco One 5.0 is available here https://github.com/Alfresco/alfresco-cloudformation-chef Please, referer to the link above for newer code and resources.

*Disclaimer:* This CloudFormation template is still in early development and should be considered for illustrative/educational purposes only. No warranty is expressed or implied. Improvements and any other contributions are encouraged and appreciated.

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

License
-------
   Copyright 2013 Alfresco Software, Ltd.
   Copyright 2013 Amazon Web Services, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

This work may reference software licensed under other open source licenses, please refer to these respective works for more information on license terms.
