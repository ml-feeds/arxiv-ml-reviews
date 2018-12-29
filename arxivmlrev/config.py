import math
from pathlib import Path
from typing import Set

import pandas as pd

CONFIG_DIR = Path(__file__).parent / '_config'
DATA_DIR = Path(__file__).parents[1] / 'data'


def _textfile_list(path: Path) -> Set[str]:
    return set(path.read_text().strip().split('\n'))


ARTICLES_PATH = DATA_DIR / 'articles.csv'
CATEGORIES = _textfile_list(Path(CONFIG_DIR) / 'categories.txt')
MAX_RESULTS_PER_QUERY = 400
DELAY_BETWEEN_QUERIES = min(3, math.ceil(math.log(MAX_RESULTS_PER_QUERY)))
TERMS = _textfile_list(Path(CONFIG_DIR) / 'terms.txt')  # Lowercase phrases without punctuation.
TERMS_BLACKLIST = _textfile_list(Path(CONFIG_DIR) / 'terms_blacklist.txt')
URL_ID_BLACKLIST = set(pd.read_csv(CONFIG_DIR / 'articles_blacklist.csv', dtype={'URL_ID': str},
                                   usecols=['URL_ID'])['URL_ID'])
