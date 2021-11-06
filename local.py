#!/usr/bin/env python3

import os
import sys
import csv
from argparse import ArgumentParser
from datetime import datetime
from update_function.gtpd_monitor.fetch import fetch_all_incidents, parse_incidents, make_incidents
from update_function.gtpd_monitor.website import gen_page, push_to_s3

def main(args):
    """
    Useful for local testing of the lambda code
    """

    parser = ArgumentParser()
    parser.add_argument('--dir', help='load csvs from directory instead')
    parser.add_argument('--html-file', help='write html to file instead')
    parser.add_argument('--csv-file', help='write csv to file instead')
    parser.add_argument('--bucket', help='s3 bucket to write to')
    parser.add_argument('--distrib-id', help='cloudfront distribution id to invalidate')
    args = parser.parse_args(args)

    # Do this once to avoid race conditions
    timestamp = datetime.now()
    this_year = timestamp.year
    this_month = timestamp.month-1

    if args.dir:
        year_incidents = {}
        for year_csv in sorted(os.listdir(args.dir)):
            if not year_csv.endswith('.csv'):
                continue

            print('parsing {}...'.format(year_csv))
            year = int(year_csv.split('.')[0])

            with open(os.path.join(args.dir, year_csv), encoding='utf-8', newline='') as fp:
                year_incidents[year] = parse_incidents(fp, year)

        incidents = make_incidents(this_year, this_month, year_incidents)
    else:
        incidents = fetch_all_incidents(this_year, this_month)

    if args.html_file:
        with open(args.html_file, 'w') as fp:
            fp.write(gen_page(incidents, timestamp))
    elif args.csv_file:
        with open(args.csv_file, 'w') as fp:
            writer = csv.writer(fp)
            writer.writerow(['Year', 'Month', 'Incidents'])
            for year, month_incidents in year_incidents.items():
                if year < incidents.start_year or year > incidents.end_year:
                    continue
                for month_idx, month_incidents in enumerate(month_incidents):
                    if year < incidents.start_year \
                       or (year == incidents.start_year and month_idx < incidents.start_month) \
                       or (year == incidents.end_year and month_idx > incidents.end_month) \
                       or year > incidents.end_year:
                        continue

                    writer.writerow([year, month_idx+1, month_incidents])
    elif args.bucket and args.distrib_id:
        push_to_s3(args.distrib_id, args.bucket, year_incidents, timestamp)
    else:
        print('incidents: {}'.format(year_incidents))

if __name__ == '__main__':
    main(sys.argv[1:])
