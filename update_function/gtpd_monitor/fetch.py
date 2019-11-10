import csv
import codecs
import contextlib
import requests
from datetime import datetime

THIS_YEAR_URL = 'https://police.gatech.edu/crimelogcsv.php'
MENTAL_HEALTH_CODE = '9999MH'
OFFENSE_CODE_COL = 'OffenseCode'
DATE_COLS = ['IncidentFromDate', 'IncidentToDate']

def fetch_incidents(year):
    r = requests.get(THIS_YEAR_URL, headers={'user-agent': 'gtpd-monitor/0.0.1'}, stream=True)
    print('status code: {}'.format(r.status_code))
    print(r.headers)
    with contextlib.closing(r):
        # 1000 IQ move to get a line-by-line iterator on the response stream.
        # unfortunately. r.iter_lines() does not work because it leaves a stray
        # 0x00 byte at the beginning of each line since 0x0a is encoded in
        # UTF-16LE as 0x0a00. annoying!!!
        fp = codecs.iterdecode(codecs.EncodedFile(r.raw, data_encoding='utf-8', file_encoding='utf-16le'), 'utf-8')
        return parse_incidents(fp, year)

def parse_incidents(fp, year):
    reader = csv.DictReader(fp)
    num_incidents = 0
    num_rows = 0

    for row in reader:
        num_rows += 1
        date_strs = [row[date_col] for date_col in DATE_COLS]
        dates = [to_datetime(date_str) for date_str in date_strs if date_str]

        # Be very conservative: start and end date must fall in this year
        wrong_years = [date.year for date in dates if date.year != year]
        if not dates:
            print('warning: row is missing any date. ignoring...')
        elif wrong_years:
            print('warning: year {} is not this year ({}). ignoring...'.format(wrong_years[0], year))
        elif row[OFFENSE_CODE_COL] == MENTAL_HEALTH_CODE:
            num_incidents += 1

    print('number of rows: {}\n'.format(num_rows))

    return num_incidents

def to_datetime(date_str):
    # 01/22/2021
    return datetime.strptime(date_str, '%m/%d/%Y')
