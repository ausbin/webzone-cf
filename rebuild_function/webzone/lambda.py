import os
from datetime import datetime
from gtpd_monitor.fetch import fetch_all_incidents
from gtpd_monitor.website import push_to_s3

def lambda_handler(event, context):
    bucket_name = os.environ['WEBSITE_BUCKET_NAME']
    distrib_id = os.environ['DISTRIBUTION_ID']
    timestamp = datetime.now()

    incidents = fetch_all_incidents(timestamp)
    push_to_s3(distrib_id, bucket_name, incidents, timestamp)
