#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from datetime import datetime
from update_function.gtpd_monitor.fetch import fetch_incidents, parse_incidents
from update_function.gtpd_monitor.website import gen_page, push_to_s3

def main(args):
    """
    Useful for local testing of the lambda code
    """

    parser = ArgumentParser()
    parser.add_argument('--file', help='load from file instead')
    parser.add_argument('--out-file', help='write html to file instead')
    parser.add_argument('--bucket', help='s3 bucket to write to')
    parser.add_argument('--distrib-id', help='cloudfront distribution id to invalidate')
    args = parser.parse_args(args)

    num_incidents = 0
    # Do this once to avoid race conditions
    timestamp = datetime.now()
    this_year = timestamp.year

    if args.file:
        with open(args.file, encoding='utf-16le', newline='') as fp:
            num_incidents = parse_incidents(fp, this_year)
    else:
        num_incidents = fetch_incidents(this_year)

    if args.out_file:
        with open(args.out_file, 'w') as fp:
            fp.write(gen_page(num_incidents, timestamp))
    elif args.bucket and args.distrib_id:
        push_to_s3(args.distrib_id, args.bucket, num_incidents, timestamp)
    else:
        print('incidents: {}'.format(num_incidents))

if __name__ == '__main__':
    main(sys.argv[1:])
