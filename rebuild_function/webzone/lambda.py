import os
import hmac
import json
from tempfile import TemporaryDirectory as TmpDir
from build import clone_shallow, hugo_build
from update import push_to_s3

def lambda_handler(event, context):
    webhook_secret = os.environ['WEBHOOK_SECRET']
    clone_url = os.environ['GIT_CLONE_URL']
    bucket_name = os.environ['WEBSITE_BUCKET_NAME']
    distrib_id = os.environ['DISTRIBUTION_ID']

    # The format is apparently
    #   sha256=9cc57f2ca39c2d81aed7e3d82af0b5711863bd3403bb8f024c4c3b4ecf9652a4
    their_hmac = event['headers']['x-hub-signature-256'].split('=', 1)[-1].lower()
    our_hmac = hmac.new(webhook_secret.encode('utf-8'), event['body'].encode('utf-8'), 'sha256').hexdigest()

    if not hmac.compare_digest(their_hmac, our_hmac):
        raise ValueError('access denied!')

    if json.loads(event['body'])['ref'] != 'refs/heads/master':
        print('ignoring push since not to master')
        return 'irrelevant ref ignored'

    with TmpDir() as repo_path, TmpDir() as hugo_out_path:
        print(f'cloning {clone_url} to {repo_path}...')
        clone_shallow(clone_url, repo_path)
        print(f'building ...')
        hugo_build(repo_path, hugo_out_path)
        push_to_s3(hugo_out_path, distrib_id, bucket_name, context.aws_request_id)

    return 'rebuilt'
