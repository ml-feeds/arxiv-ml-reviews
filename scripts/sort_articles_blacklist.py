from arxivmlrev.config import CONFIG_DIR

import pandas as pd

_PATH = CONFIG_DIR / 'articles_blacklist.csv'

df = pd.read_csv(_PATH, dtype={'URL_ID': str, 'Category': 'category'})
df_new = df.sort_values('URL_ID', ascending=False).drop_duplicates('URL_ID')
if not df.equals(df_new):
    df_new.to_csv(_PATH, index=False)
