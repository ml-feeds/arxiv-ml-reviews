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
    'arabic',
    'as a guide to',
    'assisted review',
    'automated driving',
    'autonomous driving',
    'blooms taxonomy',
    'book review',
    'cancer',
    'case study',
    'chinese',
    'competition',
    'conference',
    'discussion forum',
    'discussion threads',
    'eirex',
    'electronic health records',
    'generate review',
    'heart',
    'hindi',
    'in a taxonomy',
    'indian',
    'matlab toolbox',
    'medical guidelines',
    'movie review',
    'myocardial',
    'norwegian',
    'online reviews',
    'patent',
    'pediatrics',
    'peer review',
    'peerus review',
    'product review',
    'review based',
    'review datasets',
    'review detection',
    'review helpfulness',
    'review rating',
    'review representations',
    'review selection',
    'review scores',
    'review spammers',
    'r package',
    'sports',
    'taxonomy extraction',
    'taxonomy generation',
    'taxonomy induction',
    'taxonomy modification',
    'to guide',
    'tour problem',
    'tour recommendation',
    'tutorial generation',
    'twitter',
    'user review',
    'wikiconv',
    'wikipedia',
    'wsdm cup',
}
