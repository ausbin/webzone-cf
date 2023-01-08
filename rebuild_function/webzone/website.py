import io
import csv
import json
import boto3

JSON_FILENAME = 'incidents.json'
JSON_CONTENT_TYPE = 'application/json'
CSV_BY_MONTH_FILENAME = 'incidents_by_month.csv'
CSV_BY_HOUR_FILENAME = 'incidents_by_hour.csv'
CSV_CONTENT_TYPE = 'text/csv'

def incidents_json(incidents):
    # Need to copy this since _asdict() seems to return a mutable view of the
    # namedtuple. Crazy!
    asdict = dict(incidents._asdict())
    # Annoying, but we need to go in and manually override year_incidents
    # decaying to a tuple
    asdict['year_incidents'] = {year: incidents.year_incidents[year]._asdict()
                                for year in incidents.year_incidents}
    return json.dumps(asdict)

def incidents_by_month_csv(incidents):
    fp = io.StringIO()
    writer = csv.writer(fp)
    writer.writerow(['Year', 'Month', 'Incidents'])

    for year, year_incidents in incidents.year_incidents.items():
        if year < incidents.start_year or year > incidents.end_year:
            continue

        month_incidents = year_incidents.by_month
        for month_idx, month_incidents_ in enumerate(month_incidents):
            if (year == incidents.start_year and month_idx < incidents.start_month) \
                    or (year == incidents.end_year and month_idx > incidents.end_month):
                continue

            writer.writerow([year, month_idx+1, month_incidents_])

    return fp.getvalue()

def incidents_by_hour_csv(incidents):
    fp = io.StringIO()
    writer = csv.writer(fp)
    writer.writerow(['Year', 'Hour', 'Incidents'])

    for year, year_incidents in incidents.year_incidents.items():
        if year < incidents.start_year or year > incidents.end_year:
            continue

        hour_incidents = year_incidents.by_hour
        for hour_idx, hour_incidents_ in enumerate(hour_incidents):
            writer.writerow([year, hour_idx, hour_incidents_])

    return fp.getvalue()

def push_to_s3(distrib_id, bucket, incidents, timestamp):
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
