import csv
import codecs
import contextlib
import requests
from datetime import datetime

# Data started in 2010, but mental health code was not introduced until 2018
#START_YEAR = 2010
START_YEAR = 2018
PREV_YEAR_URL = 'https://police.gatech.edu/sites/default/files/documents/crimelogs/{year}%20Crime%20Log.csv'
THIS_YEAR_URL = 'https://police.gatech.edu/crimelogcsv.php'
MENTAL_HEALTH_CODE = '9999MH'
OFFENSE_CODE_COL = 'OffenseCode'
DATE_COLS = ['IncidentFromDate', 'IncidentToDate']

def fetch_all_incidents(this_year):
    year_incidents = {}
    for year in range(START_YEAR, this_year+1):
        year_incidents[year] = fetch_incidents(year, this_year)
    return year_incidents

def fetch_incidents(year, this_year):
    if year == this_year:
        url = THIS_YEAR_URL
    elif year < this_year:
        url = PREV_YEAR_URL.format(year=year)
    else:
        raise ValueError('year {} in future???'.format(year))

    print('fetching {}...'.format(url))

    r = requests.get(url, headers={'user-agent': 'gtpd-monitor/0.0.1'}, stream=True)
    print('status code: {}'.format(r.status_code))
    print(r.headers)

    with contextlib.closing(r):
        is_utf8, first_bytes = guess_utf8(r.raw)

        if is_utf8:
            # This concatenation is a hack to restore the bytes we already read
            # to guess the encoding
            fp = codecs.iterdecode(((first_bytes+line_bytes if i == 0 else line_bytes)
                                    for i, line_bytes in enumerate(r.raw)), 'utf-8')
        else:
            # shield your eyes
            first_bytes = first_bytes.decode('utf-16le').encode('utf-8')

            # 1000 IQ move to get a line-by-line iterator on the response stream.
            # unfortunately. r.iter_lines() does not work because it leaves a stray
            # 0x00 byte at the beginning of each line since 0x0a is encoded in
            # UTF-16LE as 0x0a00. annoying!!!
            fp = codecs.iterdecode(((first_bytes+line_bytes if i == 0 else line_bytes)
                                    for i, line_bytes in enumerate(
                                        codecs.EncodedFile(r.raw, data_encoding='utf-8',
                                                           file_encoding='utf-16le'))),
                                   'utf-8')

        return parse_incidents(fp, year)

# Unfortunately, GTPD CSVs vary in encoding. Starting in 2020, they appear to
# be in UTF-16 little endian, while the rest are encoded in UTF-8. We can make
# a pretty good guess by reading the first two bytes and seeing if the second
# is null
def guess_utf8(fp):
    first_bytes = b''.join(fp.read(1) for i in range(2))
    is_utf8 = first_bytes[1] != 0
    return is_utf8, first_bytes

def parse_incidents(fp, year):
    reader = csv.DictReader(fp)
    num_incidents = 0
    num_rows = 0

    for row in reader:
        num_rows += 1
        date_strs = [row[date_col] for date_col in DATE_COLS]
        dates = [date for date in (to_datetime(date_str) for date_str in date_strs
                                   if date_str and date_str.upper() != 'NULL')
                 if date is not None]

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
    try:
        return datetime.strptime(date_str, '%m/%d/%Y')
    except ValueError as e:
        print('invalid date format: {}'.format(e))
        return None
