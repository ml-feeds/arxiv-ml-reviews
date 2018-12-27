import arxivmlrev.config as config

from string import punctuation
import time
from types import SimpleNamespace

import arxiv

terms_quoted = {f'"{term}"' if ' ' in term else term for term in config.TERMS}
terms_blacklist_quoted = {f'"{term}"' if ' ' in term else term for term in config.TERMS_BLACKLIST}

title_query = ' OR '.join(f'ti:{term}' for term in sorted(terms_quoted))
title_query_blacklist = ' OR '.join(f'ti:{term}' for term in sorted(terms_blacklist_quoted))
cat_query = ' OR '.join(f'cat:{cat}' for cat in sorted(config.CATEGORIES))
search_query = f'({title_query}) AND ({cat_query}) ANDNOT ({title_query_blacklist})'
print(search_query)


def get_results():
    start = 0
    max_results = 480
    while True:
        for attempt in range(2):
            print(f'\nstart={start}')
            query_time = time.time()
            results = arxiv.query(search_query=search_query, start=start, max_results=max_results, sort_by='submittedDate')
            if results:
                break
            else:
                time.sleep(config.DELAY)
        else:
            return

        for result in results:
            id_ = result['id'].rsplit('/')[-1].rsplit('v')[0]
            if id_ in config.ID_BLACKLIST:
                continue
            title = result['title'].replace('\n ', '')
            title_cmp = ''.join(c for c in title.lower() if c not in punctuation)
            # if any(term in title_cmp for term in config.TERMS_BLACKLIST):
            #     print(f'SKIPPING BLACKLISTED {title}')
            #     continue
            if all(f'{term} ' not in f'{title_cmp} ' for term in config.TERMS):
                # print(f'SKIPPING NON-WHITELISTED {title}')
                continue
            year = result['published_parsed'].tm_year
            year_updated = result['updated_parsed'].tm_year
            if year != year_updated:
                year = f'{year}-{year_updated}'
            primary_category = result['arxiv_primary_category']['term']
            if primary_category not in config.CATEGORIES:
                continue
            result = {'id': id_, 'title': title, 'cat': primary_category, 'year': year}
            yield result
        start += max_results
        sleep_time = max(0, config.DELAY - (time.time() - query_time))
        time.sleep(sleep_time)


for result in get_results():
    r = SimpleNamespace(**result)
    if ',' in r.title:
        assert '"' not in r.title
        r.title = f'"{r.title}"'
    print(f'{r.id},{r.cat},{r.title}')
