from arxivmlrev.config import CATEGORIES, ID_BLACKLIST, TERMS, YEAR_MIN

from string import punctuation
from time import sleep
from types import SimpleNamespace

import arxiv

title_query = ' OR '.join(f'ti:{term}' for term in sorted(TERMS))
cat_query = ' OR '.join(f'cat:{cat}' for cat in sorted(CATEGORIES))
search_query = f'({title_query}) AND ({cat_query})'
print(search_query)


def get_results():
    start = 0
    max_results = 2000
    while True:
        print(f'\nstart={start}')
        results = arxiv.query(search_query=search_query, start=start, max_results=max_results, sort_by='submittedDate')
        for result in results:
            id_ = result['id'].rsplit('/')[-1].rsplit('v')[0]
            if id_ in ID_BLACKLIST:
                continue
            title = result['title'].replace('\n ', '')
            title_terms = set(term.rstrip(punctuation) for term in title.lower().split(' '))
            if not(TERMS & title_terms):
                continue
            year = result['published_parsed'].tm_year
            if year < YEAR_MIN:
                return
            year_updated = result['updated_parsed'].tm_year
            if year != year_updated:
                year = f'{year}-{year_updated}'
            primary_category = result['arxiv_primary_category']['term']
            if primary_category not in CATEGORIES:
                continue
            result = {'id': id_, 'title': title, 'cat': primary_category}
            yield result
        start += max_results
        sleep(4)


for result in get_results():
    r = SimpleNamespace(**result)
    if ',' in r.title:
        assert '"' not in r.title
        r.title = f'"{r.title}"'
    print(f'{r.id},{r.cat},{r.title}')
