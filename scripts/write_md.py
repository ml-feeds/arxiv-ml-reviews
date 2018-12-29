from datetime import date

from arxivmlrev import config

import pandas as pd

prologue = f"""
This is a mostly auto-generated list of review articles on machine learning that are on arXiv.
Although some of them are written for a specific technical audience or for a specific application, the techniques
described are nonetheless generally applicable.
This list was generated on {date.today()}.
It includes articles posted in these arXiv categories: {', '.join(sorted(config.CATEGORIES))}\n
"""


def write_md_file() -> None:
    df = pd.read_csv(config.DATA_DIR / 'articles.csv', dtype={'URL_ID': str, 'Category': 'category'})
    with (config.DATA_DIR / 'articles.md').open('w') as md:
        md.write(f'# Review articles\n{prologue}')
        for _, row in df.iterrows():
            years = row.Year_Published if (row.Year_Published == row.Year_Updated) else f'{row.Year_Published}-{row.Year_Updated}'
            link = f'https://arxiv.org/abs/{row.URL_ID}'
            md.write(f'* [{row.Title} ({years})]({link})\n')


if __name__ == '__main__':
    write_md_file()
