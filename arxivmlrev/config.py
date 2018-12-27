from pathlib import Path

import data

import pandas as pd

DATA_DIR = Path(data.__path__._path[0])

CATEGORIES = {
    'cs.AI',
    'cs.CL',
    'cs.IR',
    'cs.LG',
    'cs.NE',
    # 'cs.CV',
    'stat.ML',
}

DELAY = 4  # Per recommendation of 3 at https://arxiv.org/help/api/user-manual#paging

ID_BLACKLIST = set(pd.read_csv(DATA_DIR / 'blacklist.csv', dtype={'ID': str}, usecols=['ID'])['ID'])

TERMS = {  # Lowercase phrases only. Punctuation characters not allowed.
    'critical appraisal',
    'critical reflection',
    'brief history',
    'contemporary',
    'discussion',
    'introduction',
    'guide',
    'guidelines',
    'history of',
    'mathematics of',
    'overview',
    'review',
    'taxonomy',
    'tour',
    'tutorial',
}

TERMS_BLACKLIST = {  # Lowercase phrases only. Punctuation characters not allowed.
    'airline review',
    'app reviews',
    'as a guide to',
    'assisted review',
    'automated driving',
    'autonomous driving',
    'book review',
    'cancer',
    'competition',
    'conference',
    'eirex',
    'electronic health records',
    'heart',
    'in a taxonomy',
    'matlab toolbox',
    'myocardial',
    'online reviews',
    'patent',
    'pediatrics',
    'peer review',
    'peerus review',
    'review based',
    'review datasets',
    'review detection',
    'review selection',
    'review scores',
    'r package',
    'sports',
    'taxonomy generation',
    'taxonomy induction',
    'taxonomy modification',
    'to guide',
    'tour problem',
    'tour recommendation',
    'tutorial generation',
    'user review',
    'wikipedia',
    'wsdm cup',
}

YEAR_MIN = 2000  # TODO: Gradually lower.
