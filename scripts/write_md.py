from arxivmlrev.config import DATA_DIR

import pandas as pd


def write_md_file() -> None:
    df = pd.read_csv(DATA_DIR / 'whitelist.csv', dtype={'ID': str, 'Category': 'category'})
    df = df.sort_values(['Group', 'ID'], ascending=[1, 0])
    with (DATA_DIR / 'articles.md').open('w') as md:
        md.write('# Introductory articles')
        for group_name, group in df.groupby('Group'):
            md.write(f'\n## {group_name}\n')
            for _, row in group.iterrows():
                year = f'20{row.ID[:2]}'
                link = f'https://arxiv.org/abs/{row.ID}'
                md.write(f'* [{row.Title} ({year})]({link})\n')


if __name__ == '__main__':
    write_md_file()
