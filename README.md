gtpd-monitor
============

This is the CloudFormation template for a tracker for incidents in which the
Georgia Tech Police Department reported an incident tagged with the mental
health "offense code". The job runs daily. This repository uses [SAM][1], a
handy wrapper around [CloudFormation][2].

How to update:

    $ pip3 install --user --upgrade awscli aws-sam-cli
    $ ./update.sh

The first time you run this, you'll need to:

 1. Add a CNAME record for the hostname, which is needed for generating the SSL
    cert. If you go to the Events tab in the CloudFront section of the AWS
    Console for the stack, you can see what CNAME it expects
 2. Add A and AAAA records which are aliases for the CloudFront
    distribution once CloudFormation has set it up
 3. Upload the 404 page:
    `aws s3 cp 404.html s3://gtpd-monitor-website/404.html`

To locally test the lambda, you can use `./local.py`. There are various flags
that change its behavior. You can create a virtualenv (e.g., `virtualenv -p
python3 venv; . venv/bin/activate`) and use `requirements.txt` to install the
dependencies (`pip install -r update_function/requirements.txt`). There's
probably some overcomplicated SAM way to do this instead but I don't care

Links
-----

* Main link (goes through CloudFront): <https://gtpd-monitor.austinjadams.com/>
* Backup link (hits S3 directly, useful if you want to bypass CloudFront for
  debugging): <http://gtpd-monitor-website.s3-website-us-east-1.amazonaws.com/>

[1]: https://aws.amazon.com/serverless/sam/
[2]: https://aws.amazon.com/cloudformation/
