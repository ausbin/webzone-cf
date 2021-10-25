import boto3

FILENAME = 'index.html'
CONTENT_TYPE = 'text/html'
# Need to use an actual template language or react, this is getting ridiculous
PASTYEARS_SEP = ', '
PASTYEARS_TEMPLATE = '<strong>{year}:</strong> {counter}'
TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>GTPD Mental Health Calls Tracker</title>
    <style>
        html, body {{
            background-color: white;
        }}

        body {{
            max-width: 256px;
            margin: 64px auto 0 auto;

            color: black;
            font-family: sans-serif;
            font-size: 14px;
            text-align: center;
        }}

        #counter {{
            font-size: 64px;
            font-weight: bold;
        }}

        footer {{
            margin-top: 64px;
            font-size: 8px;
        }}
    </style>
</head>
<body>
    <p>GTPD Mental Health Calls Reported in <strong>{year}</strong>:</p>
    <p id="counter">{counter}</p>
    <p>Past years:<br/>{pastyears}</p>
    <footer>last updated {last_updated}. <a href="https://police.gatech.edu/crime-logs-and-map">data source</a>. <a href="https://github.com/ausbin/gtpd-counter">source code</a></footer>
</body>
</html>
'''

def push_to_s3(distrib_id, bucket, year_counters, timestamp):
    page_bytes = gen_page(year_counters, timestamp).encode('utf-8')

    s3 = boto3.resource('s3')
    s3.Bucket(bucket).put_object(Key=FILENAME, Body=page_bytes, ContentType=CONTENT_TYPE)

    cf = boto3.client('cloudfront')
    cf.create_invalidation(DistributionId=distrib_id, InvalidationBatch={
        'CallerReference': str(timestamp),
        'Paths': {
            'Quantity': 2,
            'Items': ['/', '/' + FILENAME],
        },
    })

def gen_page(year_counters, timestamp):
    this_year = timestamp.year
    pastyears = PASTYEARS_SEP.join(PASTYEARS_TEMPLATE.format(year=year, counter=counter)
                                   for year, counter in year_counters.items() if year != this_year)
    return TEMPLATE.format(year=this_year, counter=year_counters[this_year],
                           last_updated=str(timestamp), pastyears=pastyears)
