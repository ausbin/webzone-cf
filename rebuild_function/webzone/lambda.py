import os
from datetime import datetime
from tempfile import TemporaryDirectory as TmpDir
from webzone.clone import clone_shallow
from webzone.website import push_to_s3

def lambda_handler(event, context):
    clone_url = os.environ['GIT_CLONE_URL']
    bucket_name = os.environ['WEBSITE_BUCKET_NAME']
    distrib_id = os.environ['DISTRIBUTION_ID']

    with TmpDir() as repo_path, TmpDir() as hugo_path:
        clone_shallow(clone_url, repo_path)
        hugo_build(repo_path, hugo_path)
        push_to_s3(hugo_path, distrib_id, bucket_name)
