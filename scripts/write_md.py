from datetime import date

from arxivmlrev import config

import pandas as pd


categories = ', '.join(f'[{cat}](https://arxiv.org/list/{cat}/recent)' for cat in sorted(config.CATEGORIES))

prologue = f"""
This is a mostly auto-generated list of review articles on machine learning that are on arXiv.
Although some of them were written for a specific technical audience or application, the techniques described are
nonetheless generally relevant.
The list is sorted reverse chronologically. It was generated on {date.today()}.
It includes articles from these arXiv categories: {categories}\n
"""

df = pd.read_csv(config.DATA_DIR / 'articles.csv', dtype={'URL_ID': str, 'Category': 'category'})
with (config.DATA_DIR / 'articles.md').open('w') as md:
    md.write(f'# Review articles\n{prologue}')
    for _, row in df.iterrows():
        years = row.Year_Published if (row.Year_Published == row.Year_Updated) else \
            f'{row.Year_Published}-{row.Year_Updated}'
        link = f'https://arxiv.org/abs/{row.URL_ID}'
        md.write(f'* [{row.Title} ({years})]({link})\n')
