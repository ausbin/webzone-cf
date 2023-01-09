webzone Cloud Formation
=======================

This is the CloudFormation template for my [personal website][0]. This
repository uses [SAM][1], a handy wrapper around [CloudFormation][2]. The
lambda regenerates the static website assets using [Hugo][3].

For an initial setup, run:

    $ pip3 install --user --upgrade awscli aws-sam-cli

If the stack does not exist yet, create the ECR (docker image) repository:

    $ aws ecr create-repository --repository-name webzone --region us-east-1

and put the `repositoryUri` printed above in `$repository_uri` at the top of
`update.sh`. Additionally, set

    $ export WEBHOOK_SECRET=SomeSecretValue

To avoid having to do this every time, it's helpful to write `SomeSecretValue`
to `~/.webhook-secret` and then add the following to your `.bashrc`:

    read -r WEBHOOK_SECRET <~/.webhook-secret
    export WEBHOOK_SECRET

**To update**, once you've done all that:

    $ ./update.sh

Additionally, the first time you run this, you'll need to:

1. In the past, I've needed to add a CNAME record for the hostname, which is
   needed for generating the SSL cert. I went to the Events tab in the
   CloudFormation section of the AWS Console for the stack to see what CNAME it
   expects. However, I did not need that this time around, possibly because my
   domain is in Route 53?
2. Add A and AAAA records which are aliases for the CloudFront
   distribution once CloudFormation has set it up (still had to do this)
3. Go into the GitHub settings for the repository and add the URL output by
   `./update.sh` as the webhook URL. Choose "only `push`". Add the secret
   `$WEBHOOK_SECRET`.

To locally test the lambda, you can use `./test.sh`... almost. Something is
broken about connecting to CloudFront but I don't care enough to debug. It
works well enough for checking syntax errors, at least.

Links
-----

* Main link (goes through CloudFront): <https://ausb.in/>
* Backup link (hits S3 directly, useful if you want to bypass CloudFront for
  debugging): <http://austinjadams-com-website.s3-website-us-east-1.amazonaws.com/>

[0]: https://github.com/ausbin/webzone
[1]: https://aws.amazon.com/serverless/sam/
[2]: https://aws.amazon.com/cloudformation/
[3]: https://gohugo.io/
[4]: https://github.com/aws/aws-cli/issues/4947#issuecomment-586046886
