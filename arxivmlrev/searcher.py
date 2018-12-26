from arxivmlrev.config import CATEGORIES, DELAY, ID_BLACKLIST, TERMS, TERM_BLACKLIST, YEAR_MIN

from string import punctuation
import time
from types import SimpleNamespace

import arxiv

title_query = ' OR '.join(f'ti:{term}' for term in sorted(TERMS))
cat_query = ' OR '.join(f'cat:{cat}' for cat in sorted(CATEGORIES))
search_query = f'({title_query}) AND ({cat_query})'
print(search_query)


def get_results():
    start = 0
    max_results = 100
    while True:
        print(f'\nstart={start}')
        query_time = time.time()
        results = arxiv.query(search_query=search_query, start=start, max_results=max_results, sort_by='submittedDate')
        for result in results:
            id_ = result['id'].rsplit('/')[-1].rsplit('v')[0]
            if id_ in ID_BLACKLIST:
                continue
            title = result['title'].replace('\n ', '')
            title_cmp = ''.join(c for c in title.lower() if c not in punctuation)
            if any(term in title_cmp for term in TERM_BLACKLIST):
                print(f'SKIPPING {title}')
                continue
            title_terms = set(term for term in title_cmp.split(' '))
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
        sleep_time = max(0, DELAY - (time.time() - query_time))
        time.sleep(sleep_time)


for result in get_results():
    r = SimpleNamespace(**result)
    if ',' in r.title:
        assert '"' not in r.title
        r.title = f'"{r.title}"'
    print(f'{r.id},{r.cat},{r.title}')
