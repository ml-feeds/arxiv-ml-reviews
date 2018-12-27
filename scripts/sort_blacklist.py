from arxivmlrev.config import DATA_DIR

import pandas as pd

df = pd.read_csv(DATA_DIR / 'blacklist.csv', dtype={'ID': str, 'Category': 'category'})
df.sort_values('ID', ascending=False, inplace=True)
df.to_csv(DATA_DIR / 'blacklist.csv', index=False)
