import boto3

def push_to_s3(local_path, distrib_id, bucket):
    # TODO: update for webzone
    s3 = boto3.resource('s3')
    bucket_ = s3.Bucket(bucket)

    json_bytes = incidents_json(incidents).encode('utf-8')
    bucket_.put_object(Key=JSON_FILENAME, Body=json_bytes, ContentType=JSON_CONTENT_TYPE)

    csv_by_month_bytes = incidents_by_month_csv(incidents).encode('utf-8')
    bucket_.put_object(Key=CSV_BY_MONTH_FILENAME, Body=csv_by_month_bytes, ContentType=CSV_CONTENT_TYPE)

    csv_by_hour_bytes = incidents_by_hour_csv(incidents).encode('utf-8')
    bucket_.put_object(Key=CSV_BY_HOUR_FILENAME, Body=csv_by_hour_bytes, ContentType=CSV_CONTENT_TYPE)

    cf = boto3.client('cloudfront')
    cf.create_invalidation(DistributionId=distrib_id, InvalidationBatch={
        'CallerReference': str(timestamp),
        'Paths': {
            'Quantity': 3,
            'Items': ['/' + JSON_FILENAME, '/' + CSV_BY_MONTH_FILENAME, '/' + CSV_BY_HOUR_FILENAME],
        },
    })
