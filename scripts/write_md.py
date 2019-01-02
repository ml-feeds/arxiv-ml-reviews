from datetime import date
import logging

from arxivmlrev import config
from arxivmlrev.util.string import readable_list

import pandas as pd

log = logging.getLogger(__name__)


def _linked_category(cat: str) -> str:
    return f'[{cat}](https://arxiv.org/list/{cat}/recent)'


categories = readable_list(_linked_category(cat) for cat in sorted(config.CATEGORIES))

prologue = f"""
This is a mostly auto-generated list of review articles on machine learning and artificial intelligence that are on \
[arXiv](https://arxiv.org/). \
Although some of them were written for a specific technical audience or application, the techniques described are \
nonetheless generally relevant. \
The list is sorted reverse chronologically. It was generated on {date.today()}. \
It includes articles mainly from the arXiv categories {categories}. \
A rememberable short link to this page is [https://j.mp/ml-reviews](https://j.mp/ml-reviews). \
The [source code](https://github.com/impredicative/arxiv-ml-reviews) along with \
[raw data](https://raw.githubusercontent.com/impredicative/arxiv-ml-reviews/master/data/articles.csv) for generating \
this page are linked. \
This page is currently not automatically updated.
"""

df = pd.read_csv(config.DATA_ARTICLES_CSV_PATH, dtype={'URL_ID': str, 'Category': 'category'})
with config.DATA_ARTICLES_MD_PATH.open('w') as md:
    md.write(f'# Review articles\n{prologue}\n')
    for _, row in df.iterrows():
        cat = _linked_category(row.Category)
        years = row.Year_Published if (row.Year_Published == row.Year_Updated) else \
            f'{row.Year_Published}-{row.Year_Updated}'
        link = f'https://arxiv.org/abs/{row.URL_ID}'
        md.write(f'* [{row.Title} ({years})]({link}) ({cat})\n')
log.info('Finished writing markdown file.')
