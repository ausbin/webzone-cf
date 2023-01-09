#!/bin/bash
set -e -x

if [[ -z $WEBHOOK_SECRET ]]; then
    printf 'error: you need to define the environment variable $WEBHOOK_SECRET\n' >&2
    exit 2
fi

repository_uri=917270012582.dkr.ecr.us-east-1.amazonaws.com/webzone

# From https://aws.amazon.com/blogs/compute/using-container-image-support-for-aws-lambda-with-aws-sam/
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "$repository_uri"

sam build
sam package --output-template-file packaged.yaml --region us-east-1 --resolve-s3 --image-repository "$repository_uri"
sam deploy --template-file packaged.yaml --region us-east-1 \
           --image-repository "$repository_uri" \
           --stack-name webzone \
           --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
           --parameter-overrides 'WebsiteBucketName=austinjadams-com-website' \
                                 'WebsiteHostname=austinjadams.com' \
                                 'WebsiteAltHostnames=www.austinjadams.com,ausb.in,aja.gay' \
                                 'GitCloneUrl=https://github.com/ausbin/webzone.git' \
                                 "WebhookSecret=$WEBHOOK_SECRET"
