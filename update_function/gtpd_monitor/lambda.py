import os
from datetime import datetime
from gtpd_monitor.fetch import fetch_all_incidents
from gtpd_monitor.website import push_to_s3

def lambda_handler(event, context):
    bucket_name = os.environ['WEBSITE_BUCKET_NAME']
    distrib_id = os.environ['DISTRIBUTION_ID']
    timestamp = datetime.now()
    this_year = timestamp.year

    year_incidents = fetch_all_incidents(this_year)
    push_to_s3(distrib_id, bucket_name, year_incidents, timestamp)
