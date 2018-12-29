import math
from pathlib import Path
from typing import Set

import pandas as pd


def _textfile_set(path: Path) -> Set[str]:
    return set(path.read_text().strip().split('\n'))


CONFIG_DIR = Path(__file__).parent / '_config'
DATA_DIR = Path(__file__).parents[1] / 'data'

CATEGORIES = _textfile_set(Path(CONFIG_DIR) / 'categories.txt')
CONFIG_ARTICLES_PATH = CONFIG_DIR / 'articles.csv'
CONFIG_ARTICLES = pd.read_csv(CONFIG_ARTICLES_PATH, dtype={'URL_ID': str})
DATA_ARTICLES_COLUMNS = ['URL_ID', 'Category', 'Title', 'Year_Published', 'Year_Updated']
DATA_ARTICLES_PATH = DATA_DIR / 'articles.csv'
MAX_RESULTS_PER_QUERY = 400
DELAY_BETWEEN_QUERIES = min(3, math.ceil(math.log(MAX_RESULTS_PER_QUERY)))
TERMS = _textfile_set(Path(CONFIG_DIR) / 'terms.txt')  # Lowercase phrases without punctuation.
TERMS_BLACKLIST = _textfile_set(Path(CONFIG_DIR) / 'terms_blacklist.txt')
URL_ID_BLACKLIST = set(CONFIG_ARTICLES[CONFIG_ARTICLES['Presence'] == 0]['URL_ID'])
URL_ID_WHITELIST = set(CONFIG_ARTICLES[CONFIG_ARTICLES['Presence'] == 1]['URL_ID'])
