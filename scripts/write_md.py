from datetime import date

from arxivmlrev import config

import pandas as pd
import pyperclip


categories = ', '.join(f'[{cat}](https://arxiv.org/list/{cat}/recent)' for cat in sorted(config.CATEGORIES))

prologue = f"""
This is a mostly auto-generated list of review articles on machine learning and artificial intelligence that are on \
[arXiv](https://arxiv.org/). \
Although some of them were written for a specific technical audience or application, the techniques described are \
nonetheless generally relevant. \
The list is sorted reverse chronologically. It was generated on {date.today()}. \
It includes articles from these arXiv categories: {categories}
"""

df = pd.read_csv(config.DATA_ARTICLES_CSV_PATH, dtype={'URL_ID': str, 'Category': 'category'})
with config.DATA_ARTICLES_MD_PATH.open('w') as md:
    md.write(f'# Review articles\n{prologue}\n')
    for _, row in df.iterrows():
        years = row.Year_Published if (row.Year_Published == row.Year_Updated) else \
            f'{row.Year_Published}-{row.Year_Updated}'
        link = f'https://arxiv.org/abs/{row.URL_ID}'
        md.write(f'* [{row.Title} ({years})]({link})\n')

pyperclip.copy(config.DATA_ARTICLES_MD_PATH.read_text())
# Note: pyperclip requires xclip or xsel, etc.
# Refer to https://pyperclip.readthedocs.io/en/latest/introduction.html#not-implemented-error
