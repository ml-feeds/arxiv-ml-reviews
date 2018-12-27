import arxivmlrev.config as config

from string import punctuation
import time

import arxiv
import pandas as pd

terms_quoted = {f'"{term}"' if ' ' in term else term for term in config.TERMS}
terms_blacklist_quoted = {f'"{term}"' if ' ' in term else term for term in config.TERMS_BLACKLIST}

title_query = ' OR '.join(f'ti:{term}' for term in sorted(terms_quoted))
title_query_blacklist = ' OR '.join(f'ti:{term}' for term in sorted(terms_blacklist_quoted))
cat_query = ' OR '.join(f'cat:{cat}' for cat in sorted(config.CATEGORIES))
search_query = f'({title_query}) AND ({cat_query}) ANDNOT ({title_query_blacklist})'
print(search_query)


def get_results():
    start = 0
    while True:
        for attempt in range(3):
            print(f'\nstart={start}')
            query_time = time.time()
            results = arxiv.query(search_query=search_query, start=start, max_results=config.MAX_RESULTS_PER_QUERY,
                                  sort_by='submittedDate')
            if (start == 0) and (len(results) == 1):  # This is indicative of a bad result set.
                continue
            if results:
                break
            else:
                time.sleep(config.DELAY_BETWEEN_QUERIES)
        else:
            return

        for result in results:
            url_id = result['arxiv_url'].replace('http://arxiv.org/abs/', '', 1).rsplit('v', 1)[0]
            # Note: Unlike result['id'], url_id is actually unique, specifically for results older than 2007.
            if url_id in config.URL_ID_BLACKLIST:
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
            result = {'url_id': url_id, 'cat': primary_category, 'title': title,  'years': year}
            yield result

        print(f'num_results={len(results)}')
        if len(results) < config.MAX_RESULTS_PER_QUERY:
            return
        start += config.MAX_RESULTS_PER_QUERY
        sleep_time = max(0, config.DELAY_BETWEEN_QUERIES - (time.time() - query_time))
        time.sleep(sleep_time)


for result in get_results():
    result = pd.DataFrame([result])[list(result.keys())].to_csv(header=False, index=False, line_terminator='')
    print(result)
