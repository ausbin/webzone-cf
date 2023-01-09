Webzone Cloud Formation
=======================

This is the CloudFormation template for my [personal website][0]. This
repository uses [SAM][1], a handy wrapper around [CloudFormation][2]. The
lambda regenerates the static website assets using [Hugo][3].

For an initial setup, run:

    $ pip3 install --user --upgrade awscli aws-sam-cli
    $ aws ecr create-repository --repository-name webzone --region us-east-1

Make note of the `repositoryUri` printed above and update `$repository_uri` at
the top of `update.sh`. If this is a fresh clone of this repo and the repo
already exists, `aws ecr describe-repositories --region us-east-1` could help
find the URI.

To update:

    $ ./update.sh

Additionally, the first time you run this, you'll need to:

1. Add a CNAME record for the hostname, which is needed for generating the SSL
   cert. If you go to the Events tab in the CloudFront section of the AWS
   Console for the stack, you can see what CNAME it expects
2. Add A and AAAA records which are aliases for the CloudFront
   distribution once CloudFormation has set it up

To locally test the lambda, you can use `./local.py` inside `webzone/`. There
are various flags that change its behavior. You can create a virtualenv (e.g.,
`virtualenv -p python3 venv; . venv/bin/activate`) and use `requirements.txt`
to install the dependencies (`pip install -r update_function/requirements.txt`).
There's probably some overcomplicated SAM way to do this instead but I don't care

Links
-----

* Main link (goes through CloudFront): <https://gtpd-monitor.austinjadams.com/>
* Backup link (hits S3 directly, useful if you want to bypass CloudFront for
  debugging): <http://gtpd-monitor-website.s3-website-us-east-1.amazonaws.com/>

[0]: https://github.com/ausbin/webzone
[1]: https://aws.amazon.com/serverless/sam/
[2]: https://aws.amazon.com/cloudformation/
[3]: https://gohugo.io/
[4]: https://github.com/aws/aws-cli/issues/4947#issuecomment-586046886
