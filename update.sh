#!/bin/bash
set -e -x

# TODO: update me according to the README!
repository_uri=55555.dkr.ecr.us-east-1.amazonaws.com/FIXME

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "$repository_uri"

sam build
sam package --output-template-file packaged.yaml --region us-east-1 --resolve-s3 --image-repository "$repository_uri"
sam deploy --template-file packaged.yaml --region us-east-1 \
           --stack-name webzone \
           --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
           --parameter-overrides 'WebsiteBucketName=austinjadams-com-website' \
                                 'WebsiteHostname=ausb.in' \
                                 'GitCloneUrl=https://github.com/ausbin/webzone.git' \
