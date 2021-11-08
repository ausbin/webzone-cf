import io
import csv
import json
import boto3

JSON_FILENAME = 'incidents.json'
JSON_CONTENT_TYPE = 'application/json'
CSV_FILENAME = 'incidents.csv'
CSV_CONTENT_TYPE = 'text/csv'

def incidents_json(incidents):
    return json.dumps(incidents._asdict())

def incidents_csv(incidents):
    fp = io.StringIO()
    writer = csv.writer(fp)
    writer.writerow(['Year', 'Month', 'Incidents'])

    for year, month_incidents in incidents.year_incidents.items():
        if year < incidents.start_year or year > incidents.end_year:
            continue
        for month_idx, month_incidents in enumerate(month_incidents):
            if year < incidents.start_year \
               or (year == incidents.start_year and month_idx < incidents.start_month) \
               or (year == incidents.end_year and month_idx > incidents.end_month) \
               or year > incidents.end_year:
                continue

            writer.writerow([year, month_idx+1, month_incidents])

    return fp.getvalue()

def push_to_s3(distrib_id, bucket, incidents, timestamp):
    s3 = boto3.resource('s3')
    bucket_ = s3.Bucket(bucket)

    json_bytes = incidents_json(incidents).encode('utf-8')
    bucket_.put_object(Key=JSON_FILENAME, Body=json_bytes, ContentType=JSON_CONTENT_TYPE)

    csv_bytes = incidents_csv(incidents).encode('utf-8')
    bucket_.put_object(Key=CSV_FILENAME, Body=csv_bytes, ContentType=CSV_CONTENT_TYPE)

    cf = boto3.client('cloudfront')
    cf.create_invalidation(DistributionId=distrib_id, InvalidationBatch={
        'CallerReference': str(timestamp),
        'Paths': {
            'Quantity': 2,
            'Items': ['/' + JSON_FILENAME, '/' + CSV_FILENAME],
        },
    })
