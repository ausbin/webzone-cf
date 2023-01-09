#!/usr/bin/env python3

import os
import sys
import csv
from argparse import ArgumentParser
from datetime import datetime
from update_function.gtpd_monitor.fetch import fetch_all_incidents, parse_incidents, make_incidents
from update_function.gtpd_monitor.website import push_to_s3, incidents_json, incidents_by_month_csv, incidents_by_hour_csv

def main(args):
    """
    Useful for local testing of the lambda code
    """

    parser = ArgumentParser()
    parser.add_argument('--dir', help='load csvs from directory instead')
    parser.add_argument('--month-csv-file', help='write by-month csv to file instead')
    parser.add_argument('--hour-csv-file', help='write by-month csv to file instead')
    parser.add_argument('--json-file', help='write json to file instead')
    parser.add_argument('--bucket', help='s3 bucket to write to')
    parser.add_argument('--distrib-id', help='cloudfront distribution id to invalidate')
    args = parser.parse_args(args)

    # Do this once to avoid race conditions
    timestamp = datetime.now()

    if args.dir:
        year_incidents = {}
        for year_csv in sorted(os.listdir(args.dir)):
            if not year_csv.endswith('.csv'):
                continue

            print('parsing {}...'.format(year_csv))
            year = int(year_csv.split('.')[0])

            with open(os.path.join(args.dir, year_csv), encoding='utf-8', newline='') as fp:
                year_incidents[year] = parse_incidents(fp, year)

        incidents = make_incidents(timestamp, year_incidents)
    else:
        incidents = fetch_all_incidents(timestamp)

    if args.json_file:
        with open(args.json_file, 'w') as fp:
            fp.write(incidents_json(incidents));
    elif args.month_csv_file:
        with open(args.month_csv_file, 'w') as fp:
            fp.write(incidents_by_month_csv(incidents))
    elif args.hour_csv_file:
        with open(args.hour_csv_file, 'w') as fp:
            fp.write(incidents_by_hour_csv(incidents))
    elif args.bucket and args.distrib_id:
        push_to_s3(args.distrib_id, args.bucket, incidents, timestamp)
    else:
        print('incidents: {}'.format(incidents))

if __name__ == '__main__':
    main(sys.argv[1:])
