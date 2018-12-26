from pathlib import Path

import data

import pandas as pd

DATA_DIR = Path(data.__path__._path[0])


def write_md_file() -> None:
    df = pd.read_csv(DATA_DIR / 'whitelist.csv', dtype={'ID': str, 'Group': 'category'})
    df = df.sort_values(['Group', 'ID'], ascending=[1, 0])
    with (DATA_DIR / 'articles.md').open('w') as md:
        write = md.write
        for group_name, group in df.groupby('Group'):
            write(f'\n## {group_name}\n')
            for _, row in group.iterrows():
                year = f'20{row.ID[:2]}'
                link = f'https://arxiv.org/abs/{row.ID}'
                write(f'* [{row.Title} ({year})]({link})\n')


if __name__ == '__main__':
    write_md_file()
