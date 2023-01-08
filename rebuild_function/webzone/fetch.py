import csv
import codecs
import contextlib
import requests
from datetime import datetime
from collections import namedtuple

# Data started in 2010, but mental health code was not introduced until 2018
#START_YEAR = 2010
# Mental health code started being used in June 2018
START_YEAR_MONTH = 5
START_YEAR = 2018
PREV_YEAR_URL = 'https://police.gatech.edu/sites/default/files/documents/crimelogs/{year}%20Crime%20Log.csv'
THIS_YEAR_URL = 'https://police.gatech.edu/crimelogcsv.php'
MENTAL_HEALTH_CODE = '9999MH'
OFFENSE_CODE_COL = 'OffenseCode'
FROM_DATE_COL = 'IncidentFromDate'
FROM_TIME_COL = 'IncidentFromTime'

YearIncidents = namedtuple('YearIncidents', ['by_month', 'by_hour'])
Incidents = namedtuple('Incidents', ['start_year', 'start_month', 'end_year', 'end_month', 'year_incidents', 'last_updated', 'offense_code'])

def fetch_all_incidents(timestamp):
    this_year = timestamp.year
    year_incidents = {}
    for year in range(START_YEAR, this_year+1):
        year_incidents[year] = fetch_incidents(year, this_year)
    return make_incidents(timestamp, year_incidents)

def make_incidents(timestamp, year_incidents):
    this_year = timestamp.year
    this_month = timestamp.month
    return Incidents(start_year=START_YEAR, start_month=START_YEAR_MONTH,
                     end_year=this_year, end_month=this_month,
                     year_incidents=year_incidents,
                     last_updated=timestamp.isoformat(' ', 'minutes'),
                     offense_code=MENTAL_HEALTH_CODE)

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

# Expects to be already decoded properly
def parse_incidents(fp, year):
    reader = csv.DictReader(fp)
    month_incidents = [0]*12
    hour_incidents = [0]*24
    num_rows = 0

    for row in reader:
        num_rows += 1
        date_str, time_str = row[FROM_DATE_COL], row[FROM_TIME_COL]
        date = None if {'NULL', ''} & {date_str.upper(), time_str.upper()} else to_datetime(date_str, time_str)
        if not date:
            print('warning: row {} is missing a date or time. ignoring...'.format(num_rows))
        elif date.year != year:
            print('warning: row {} year {} is not this year ({}). ignoring...'.format(num_rows, wrong_years[0], year))
        elif row[OFFENSE_CODE_COL] == MENTAL_HEALTH_CODE:
            month_incidents[date.month-1] += 1
            hour_incidents[date.hour] += 1

    print('number of rows: {}\n'.format(num_rows))

    return YearIncidents(by_month=month_incidents, by_hour=hour_incidents)

def to_datetime(date_str, time_str):
    # Date looks like: 01/22/2021
    # Time looks like: 02:32:01
    try:
        return datetime.strptime(date_str + ' ' + time_str, '%m/%d/%Y %H:%M:%S')
    except ValueError as e:
        print('invalid date format: {}'.format(e))
        return None
