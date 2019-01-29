import datetime
import logging.config
import math
import os
from pathlib import Path
from typing import Set

import pandas as pd


def _textfile_set(path: Path) -> Set[str]:
    return set(path.read_text().strip().split('\n'))


def configure_logging() -> None:
    logging.config.dictConfig(LOGGING)
    log = logging.getLogger(__name__)
    log.debug('Logging is configured.')


CONFIG_DIR = Path(__file__).parent / '_config'
DATA_DIR = Path(__file__).parents[1] / 'data'
PACKAGE_NAME = Path(__file__).parent.stem

CATEGORIES = _textfile_set(Path(CONFIG_DIR) / 'categories.txt')
CONFIG_ARTICLES_PATH = CONFIG_DIR / 'articles.csv'
CONFIG_ARTICLES = pd.read_csv(CONFIG_ARTICLES_PATH, dtype={'URL_ID': str})
CONFIG_TERMS_PATH = CONFIG_DIR / 'terms.csv'
CONFIG_TERMS = pd.read_csv(CONFIG_TERMS_PATH)
DATA_ARTICLES_CSV_COLUMNS = ['URL_ID', 'Category', 'Title', 'Year_Published', 'Year_Updated', 'Abstract']
DATA_ARTICLES_CSV_PATH = DATA_DIR / 'articles.csv'
DATA_ARTICLES_MD_PATH = DATA_DIR / 'articles.md'
FEED_CACHE_TTL = datetime.timedelta(hours=23).total_seconds()
FEED_DESCRIPTION = 'Review articles on machine learning and artificial intelligence that are on arXiv. ' \
                   'As a disclaimer, this feed has no affiliation with arXiv.'
FEED_NUM_ITEMS = 20
FEED_SOURCE_URL = 'https://arxiv.org/'
FEED_TITLE = 'arXiv ML/AI reviews (unaffiliated)'
GITHUB_ACCESS_TOKEN_PATH = Path('~/.config/github').expanduser()
GITHUB_MD_PUBLISH_PATH = 'Resources/ArticlesReview.md'
GITHUB_PUBLISH_REPO = 'freenode-machinelearning/freenode-machinelearning.github.io'
LOGGING_CONF_PATH = CONFIG_DIR / 'logging.conf'
MAX_RESULTS_PER_QUERY = 2000 - 2
MIN_INTERVAL_BETWEEN_QUERIES = max(3., math.log(MAX_RESULTS_PER_QUERY))
SOURCE_TZ_NAME = 'US/Eastern'
TERMS_BLACKLIST = set(CONFIG_TERMS[CONFIG_TERMS['Presence'] == 0]['Term'])
TERMS_WHITELIST = set(CONFIG_TERMS[CONFIG_TERMS['Presence'] == 1]['Term'])  # Lowercase phrases without punctuation.
URL_ID_BLACKLIST = set(CONFIG_ARTICLES[CONFIG_ARTICLES['Presence'] == 0]['URL_ID'])
URL_ID_WHITELIST = set(CONFIG_ARTICLES[CONFIG_ARTICLES['Presence'] == 1]['URL_ID'])
URL_ID_WHITELIST_INTERSECTION_IGNORED = ['1707.08561']


ON_SERVERLESS = bool(os.getenv('GCLOUD_PROJECT'))

TZ_NAME = 'US/Pacific'

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
        PACKAGE_NAME: {
            'level': 'INFO' if ON_SERVERLESS else 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        '': {
            'level': 'DEBUG',
            'handlers': ['console'],
         },
    },
}

configure_logging()
