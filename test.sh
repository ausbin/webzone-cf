#!/bin/bash
set -e -x

if [[ -z $WEBHOOK_SECRET ]]; then
    printf 'error: you need to define the environment variable $WEBHOOK_SECRET\n' >&2
    exit 2
fi

sam build
sam local invoke --parameter-overrides 'WebsiteBucketName=austinjadams-com-website' \
                                       'WebsiteHostname=ausb.in' \
                                       'GitCloneUrl=https://github.com/ausbin/webzone.git' \
                                       "WebhookSecret=$WEBHOOK_SECRET"
