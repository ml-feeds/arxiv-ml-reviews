import time
from typing import Set

import arxiv
import pandas as pd

from arxivmlrev import config
from arxivmlrev.result import Result

url_id_blacklist = config.URL_ID_BLACKLIST.copy()


def _set_query(strset: Set[str], prefix: str) -> str:
    strset = {f'"{s}"' if ' ' in s else s for s in strset}
    strset = ' OR '.join(f'{prefix}:{s}' for s in sorted(strset))
    return f'({strset})'


def _get_results():
    title_whitelist_query = _set_query(config.TERMS_WHITELIST, 'ti')
    title_blacklist_query = _set_query(config.TERMS_BLACKLIST, 'ti')
    id_whitelist_query = _set_query(config.URL_ID_WHITELIST, 'id')
    id_blacklist_query = _set_query(config.URL_ID_BLACKLIST, 'id')
    category_query = _set_query(config.CATEGORIES, 'cat')
    # Note: Blacklists have precedence over whitelists in the query below.
    search_query = f'''
    (
        (
            {category_query}
            AND {title_whitelist_query}
            ANDNOT {title_blacklist_query}
        )
        OR {id_whitelist_query}
    )
    ANDNOT {id_blacklist_query}
    '''
    print(search_query)
    search_query = search_query.replace('\n', ' ')

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
            result = Result(result)
            if not (result.is_id_whitelisted or result.is_title_whitelisted):
                continue  # Skip erroneous match, e.g. having "tours" in title for search term "tour".

            # ignored_categories = config.CATEGORIES - set(('cs.CV',))
            # if ('cs.CV' in categories) and not(categories & ignored_categories):
            #     pass
            # else:
            #     continue

            yield result.to_dict

        print(f'num_results={len(results)}')
        if len(results) < config.MAX_RESULTS_PER_QUERY:
            return
        start += config.MAX_RESULTS_PER_QUERY
        sleep_time = max(0, config.DELAY_BETWEEN_QUERIES - (time.time() - query_time))
        time.sleep(sleep_time)


def main():
    df = pd.DataFrame(_get_results())
    df = df[config.DATA_ARTICLES_COLUMNS]
    df.to_csv(config.DATA_ARTICLES_PATH, index=False)


if __name__ == '__main__':
    main()
