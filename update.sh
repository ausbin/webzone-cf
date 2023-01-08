#!/bin/bash
set -e -x

sam build
sam package --output-template-file packaged.yaml --region us-east-1 --resolve-s3
sam deploy --template-file packaged.yaml --region us-east-1 \
           --stack-name webzone \
           --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
           --parameter-overrides 'WebsiteBucketName=austinjadams-com-website' \
                                 'WebsiteHostname=ausb.in' \
