from arxivmlrev.config import CONFIG_DIR

import pandas as pd

_PATH = CONFIG_DIR / 'articles_blacklist.csv'

df = pd.read_csv(_PATH, dtype={'URL_ID': str, 'Category': 'category'})
df.sort_values('URL_ID', ascending=False, inplace=True)
df.drop_duplicates('URL_ID', inplace=True)
df.to_csv(_PATH, index=False)
