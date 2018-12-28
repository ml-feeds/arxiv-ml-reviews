from pathlib import Path
from typing import List

import pandas as pd

CONFIG_DIR = Path(__file__).parent / '_config'
DATA_DIR = Path(__file__).parents[1] / 'data'


def _textfile_list(path: Path) -> List[str]:
    return sorted(path.read_text().strip().split('\n'))


CATEGORIES = _textfile_list(Path(CONFIG_DIR) / 'categories.txt')
DELAY_BETWEEN_QUERIES = 4  # Per recommendation of 3 at https://arxiv.org/help/api/user-manual#paging
MAX_RESULTS_PER_QUERY = 400
TERMS = _textfile_list(Path(CONFIG_DIR) / 'terms.txt')  # Lowercase phrases without punctuation.
TERMS_BLACKLIST = _textfile_list(Path(CONFIG_DIR) / 'terms_blacklist.txt')
URL_ID_BLACKLIST = set(pd.read_csv(CONFIG_DIR / 'articles_blacklist.csv', dtype={'URL_ID': str},
                                   usecols=['URL_ID'])['URL_ID'])
