import os
from datetime import datetime
from gtpd_monitor.fetch import fetch_all_incidents
from gtpd_monitor.website import push_to_s3

def lambda_handler(event, context):
    bucket_name = os.environ['WEBSITE_BUCKET_NAME']
    distrib_id = os.environ['DISTRIBUTION_ID']
    timestamp = datetime.now()
    this_year = timestamp.year
    this_month = timestamp.month-1

    incidents = fetch_all_incidents(this_year, this_month)
    push_to_s3(distrib_id, bucket_name, incidents, timestamp)
