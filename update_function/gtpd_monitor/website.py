import json
import boto3

FILENAME = 'incidents.json'
CONTENT_TYPE = 'application/json'

def incidents_json(incidents):
    return json.dumps(incidents._asdict())

def push_to_s3(distrib_id, bucket, incidents, timestamp):
    json_bytes = incidents_json(incidents).encode('utf-8')

    s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(Key=FILENAME, Body=json_bytes, ContentType=CONTENT_TYPE)

    cf = boto3.client('cloudfront')
    cf.create_invalidation(DistributionId=distrib_id, InvalidationBatch={
        'CallerReference': str(timestamp),
        'Paths': {
            'Quantity': 1,
            'Items': ['/' + FILENAME],
        },
    })
