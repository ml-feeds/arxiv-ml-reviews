from pathlib import Path

import data

CATEGORIES = {
    'cs.AI',
    # 'cs.CL',
    'cs.IR',
    'cs.LG',
    'cs.NE',
    # 'cs.CV',
    'stat.ML',
}

DATA_DIR = Path(data.__path__._path[0])

TERMS = {
    'contemporary',
    'introduction',
    'guide',
    'overview',
    'review',
    'tour',
    'tutorial',
}

TERMS_BLACKLIST = ()