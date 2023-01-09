import os
from tempfile import TemporaryDirectory as TmpDir
from build import clone_shallow, hugo_build
from update import push_to_s3

def lambda_handler(event, context):
    clone_url = os.environ['GIT_CLONE_URL']
    bucket_name = os.environ['WEBSITE_BUCKET_NAME']
    distrib_id = os.environ['DISTRIBUTION_ID']

    with TmpDir() as repo_path, TmpDir() as hugo_out_path:
        print(f'cloning {clone_url} to {repo_path}...')
        clone_shallow(clone_url, repo_path)
        print(f'building ...')
        hugo_build(repo_path, hugo_out_path)
        push_to_s3(hugo_out_path, distrib_id, bucket_name, context.aws_request_id)
