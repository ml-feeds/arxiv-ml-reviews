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

DELAY = 3  # Per recommendation at https://arxiv.org/help/api/user-manual#paging

ID_BLACKLIST = set(pd.read_csv(DATA_DIR / 'blacklist.csv', dtype={'ID': str}, usecols=['ID'])['ID'])

TERMS = {  # Lowercase only. Punctuation characters not allowed.
    'contemporary',
    'introduction',
    'guide',
    'overview',
    'review',
    'tour',
    'tutorial',
}

TERM_BLACKLIST = {  # Lowercase only. Punctuation characters not allowed.
    'as a guide to',
    'assisted review',
    'autonomous driving',
    'cancer',
    'competition',
    'pediatrics',
    'peer review',
    'peerus review',
    'review selection',
    'sports',
    'to guide',
    'tutorial generation',
    'wsdm cup',
}

YEAR_MIN = 2014
