from pathlib import Path

import data

import pandas as pd

DATA_DIR = Path(data.__path__._path[0])

CATEGORIES = {
    'cs.AI',
    # 'cs.CL',
    'cs.IR',
    'cs.LG',
    'cs.NE',
    # 'cs.CV',
    'stat.ML',
}

ID_BLACKLIST = set(pd.read_csv(DATA_DIR / 'blacklist.csv', dtype={'ID': str}, usecols=['ID'])['ID'])

TERMS = {
    'contemporary',
    'introduction',
    'guide',
    'overview',
    'review',
    'tour',
    'tutorial',
}

TERMS_BLACKLIST = {
    'as a guide to',
    'java',
    'autonomous driving'
}

YEAR_MIN = 2014
