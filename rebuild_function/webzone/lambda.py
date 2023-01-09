import os
import hashlib
from tempfile import TemporaryDirectory as TmpDir
from build import clone_shallow, hugo_build
from update import push_to_s3

def lambda_handler(event, context):
    webhook_secret = os.environ['WEBHOOK_SECRET']
    clone_url = os.environ['GIT_CLONE_URL']
    bucket_name = os.environ['WEBSITE_BUCKET_NAME']
    distrib_id = os.environ['DISTRIBUTION_ID']

    if context['headers']['x-hub-signature-256'].lower() != hashlib.sha256(webhook_secret).hexdigest():
        raise ValueError('access denied!')

    if context['body']['ref'] != 'refs/heads/master':
        print('ignoring push since not to master')
        return 'irrelevant ref ignored'

    with TmpDir() as repo_path, TmpDir() as hugo_out_path:
        print(f'cloning {clone_url} to {repo_path}...')
        clone_shallow(clone_url, repo_path)
        print(f'building ...')
        hugo_build(repo_path, hugo_out_path)
        push_to_s3(hugo_out_path, distrib_id, bucket_name, context.aws_request_id)

    return 'rebuilt'
