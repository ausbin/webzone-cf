#!/bin/bash
set -e -x

sam build
sam local invoke --parameter-overrides 'WebsiteBucketName=austinjadams-com-website' \
                                       'WebsiteHostname=ausb.in' \
                                       'GitCloneUrl=https://github.com/ausbin/webzone.git'
