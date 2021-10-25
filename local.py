#!/usr/bin/env python3

import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from update_function.gtpd_monitor.fetch import fetch_all_incidents, parse_incidents
from update_function.gtpd_monitor.website import gen_page, push_to_s3

def main(args):
    """
    Useful for local testing of the lambda code
    """

    parser = ArgumentParser()
    parser.add_argument('--dir', help='load csvs from directory instead')
    parser.add_argument('--out-file', help='write html to file instead')
    parser.add_argument('--bucket', help='s3 bucket to write to')
    parser.add_argument('--distrib-id', help='cloudfront distribution id to invalidate')
    args = parser.parse_args(args)

    # Do this once to avoid race conditions
    timestamp = datetime.now()
    this_year = timestamp.year

    if args.dir:
        year_incidents = {}
        for year_csv in sorted(os.listdir(args.dir)):
            if not year_csv.endswith('.csv'):
                continue

            print('parsing {}...'.format(year_csv))
            year = int(year_csv.split('.')[0])

            with open(os.path.join(args.dir, year_csv), encoding='utf-8', newline='') as fp:
                year_incidents[year] = parse_incidents(fp, year)
    else:
        year_incidents = fetch_all_incidents(this_year)

    if args.out_file:
        with open(args.out_file, 'w') as fp:
            fp.write(gen_page(year_incidents, timestamp))
    elif args.bucket and args.distrib_id:
        push_to_s3(args.distrib_id, args.bucket, year_incidents, timestamp)
    else:
        print('incidents: {}'.format(year_incidents))

if __name__ == '__main__':
    main(sys.argv[1:])
