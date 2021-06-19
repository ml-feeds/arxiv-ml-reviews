import datetime
import json
import logging.config
import os
from pathlib import Path
import re
from typing import Dict, List, Pattern

import pandas as pd
from ruamel.yaml import YAML


def _terms_blacklist_regex(terms: List[str]) -> Pattern:
    pattern = '|'.join(re.escape(term) for term in terms)
    pattern = fr'\b(?i:{pattern})\b'
    return re.compile(pattern)


def _term_whitelist_regex(term: str, assertions: Dict[str, List[str]]) -> Pattern:
    escape = re.escape
    pattern = escape(term)

    if assertions:
        neg_lookbehinds = assertions.get('startswithout') or []
        if neg_lookbehinds:
            neg_lookbehinds_str = ''.join(fr'(?<!{escape(f"{s} ")})' for s in neg_lookbehinds)
            pattern = f'{neg_lookbehinds_str}{pattern}'

        neg_lookaheads = assertions.get('endswithout') or []
        if neg_lookaheads:
            neg_lookaheads_str = '|'.join(escape(s) for s in neg_lookaheads)
            pattern = fr'{pattern}(?!\ (?:{neg_lookaheads_str})\b)'

    pattern = fr'\b(?i:{pattern})\b'
    return re.compile(pattern)


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(__name__)
    log.debug('Logging is configured.')


CONFIG_DIR = Path(__file__).parent / '_config'
DATA_DIR = Path(__file__).parents[1] / 'data'
PACKAGE_NAME = Path(__file__).parent.stem

CATEGORIES_PATH = CONFIG_DIR / 'categories.txt'
CATEGORIES = sorted(set(CATEGORIES_PATH.read_text().strip().split('\n')))
CONFIG_ARTICLES_PATH = CONFIG_DIR / 'articles.csv'
CONFIG_ARTICLES = pd.read_csv(CONFIG_ARTICLES_PATH, dtype={'URL_ID': str})
DATA_ARTICLES_COLUMNS = ['URL_ID', 'Version', 'Published', 'Updated', 'Title', 'Match', 'Categories', 'Abstract']
DATA_ARTICLES_CSV_COLUMNS = [c for c in DATA_ARTICLES_COLUMNS if c != 'Abstract']
DATA_ARTICLES_CSV_PATH = DATA_DIR / 'articles.csv'
DATA_ARTICLES_MD_PATH = DATA_DIR / 'articles.md'
FEED_CACHE_TTL = datetime.timedelta(hours=23).total_seconds()
FEED_DESCRIPTION = 'Review articles on machine learning and artificial intelligence that are on arXiv. ' \
                   'As a disclaimer, this feed has no affiliation with arXiv.'
FEED_NUM_ITEMS = 30
FEED_TITLE = 'arXiv ML/AI reviews (unaffiliated)'
GITHUB_MD_PUBLISH_PATH = 'Resources/ArticlesReview.md'
GITHUB_PUBLISH_REPO = 'libera-machinelearning/libera-machinelearning.github.io'
LOGGING_CONF_PATH = CONFIG_DIR / 'logging.conf'
MAX_RESULTS_PER_QUERY = 2000 - 2
MAX_QUERY_ATTEMPTS = 10
ON_SERVERLESS = bool(os.getenv('GCLOUD_PROJECT'))  # Approximation.
QUERY_INTERVAL = 3
REPO_URL = 'https://github.com/ml-feeds/arxiv-ml-reviews'
TERMS_PATH = CONFIG_DIR / 'terms.yml'
TERMS = json.loads(json.dumps(YAML().load(TERMS_PATH)))
TERMS_BLACKLIST = sorted(set(TERMS['blacklist']))
TERMS_WHITELIST = sorted(TERMS['whitelist'])
TERMS_BLACKLIST_REGEX = _terms_blacklist_regex(TERMS['blacklist'])
TERMS_WHITELIST_REGEXES = [_term_whitelist_regex(term, assertions) for term, assertions in TERMS['whitelist'].items()]
URL_ID_BLACKLIST = set(CONFIG_ARTICLES[CONFIG_ARTICLES['Presence'] == 0]['URL_ID'])
URL_ID_WHITELIST = set(CONFIG_ARTICLES[CONFIG_ARTICLES['Presence'] == 1]['URL_ID'])
URL_ID_WHITELIST_INTERSECTION_IGNORED = ['1707.08561', '1902.01724']

LOGGING = {  # Ref: https://docs.python.org/3/howto/logging.html#configuring-logging
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(name)s:%(lineno)d:%(funcName)s:%(levelname)s: %(message)s',
        },
        'serverless': {
            'format': '%(thread)x:%(name)s:%(lineno)d:%(funcName)s:%(levelname)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'serverless' if ON_SERVERLESS else 'detailed',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        'arxiv': {
            'level': 'WARNING',
            'handlers': ['console'],
         },
        PACKAGE_NAME: {
            'level': 'INFO' if ON_SERVERLESS else 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        '': {
            'level': 'INFO',
            'handlers': ['console'],
         },
    },
}

configure_logging()
