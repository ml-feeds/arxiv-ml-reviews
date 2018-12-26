from pathlib import Path

import data

DATA_DIR = Path(data.__path__._path[0])

SUBJECTS = ('cs.AI', 'cs.CL', 'cs.LG', 'cs.NE', 'cs.CV', 'stat.ML',)

TERMS = (
    'contemporary',
    'introduction',
    'guide',
    'overview',
    'review',
    'tour',
    'tutorial',
)
