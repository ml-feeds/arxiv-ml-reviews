import time
from typing import Set

import arxiv
import pandas as pd

from arxivmlrev import config
from arxivmlrev.result import Result

url_id_blacklist = config.URL_ID_BLACKLIST.copy()


def _set_query(strset: Set[str], prefix: str) -> str:
    strset = {f'"{s}"' if ' ' in s else s for s in strset}
    return ' OR '.join(f'{prefix}:{s}' for s in sorted(strset))


def _get_results():
    title_whitelist_query = _set_query(config.TERMS_WHITELIST, 'ti')
    title_blacklist_query = _set_query(config.TERMS_BLACKLIST, 'ti')
    cat_query = _set_query(config.CATEGORIES, 'cat')
    # Note: Blacklist has implicit precedence over whitelist in the execution of the search query below.
    search_query = f'({title_whitelist_query}) AND ({cat_query}) ANDNOT ({title_blacklist_query})'
    print(search_query)

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
            # Note: Whitelist has precedence over blacklist in the checks below.
            if (not result.is_id_whitelisted) and result.is_id_blacklisted:
                url_id_blacklist.remove(result.url_id)
                continue
            if (not result.is_id_whitelisted) and (not result.is_title_whitelisted):
                continue

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
    if url_id_blacklist:
        print(f'Unnecessary IDs in articles blacklist: {", ".join(url_id_blacklist)}')


if __name__ == '__main__':
    main()

# TODO: Use config articles whitelist.
