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

DELAY = 3  # Per https://arxiv.org/help/api/user-manual#paging

ID_BLACKLIST = set(pd.read_csv(DATA_DIR / 'blacklist.csv', dtype={'ID': str}, usecols=['ID'])['ID'])

TERMS = {  # Punctuation characters not allowed.
    'contemporary',
    'introduction',
    'guide',
    'overview',
    'review',
    'tour',
    'tutorial',
}

TERM_BLACKLIST = {  # Punctuation characters not allowed.
    'agi containment',
    'as a guide to',
    'autonomous driving',
    'cancer',
    'competition',
    'sports',
}

YEAR_MIN = 2014
