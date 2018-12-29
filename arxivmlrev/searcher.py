from arxivmlrev import config
from arxivmlrev.result import Result

import time

import arxiv
import pandas as pd

url_id_blacklist = config.URL_ID_BLACKLIST.copy()


def get_results():

    terms_quoted = {f'"{term}"' if ' ' in term else term for term in config.TERMS}
    terms_blacklist_quoted = {f'"{term}"' if ' ' in term else term for term in config.TERMS_BLACKLIST}

    title_query = ' OR '.join(f'ti:{term}' for term in sorted(terms_quoted))
    title_query_blacklist = ' OR '.join(f'ti:{term}' for term in sorted(terms_blacklist_quoted))
    cat_query = ' OR '.join(f'cat:{cat}' for cat in sorted(config.CATEGORIES))
    search_query = f'({title_query}) AND ({cat_query}) ANDNOT ({title_query_blacklist})'
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
            # Note: Whitelist has precedence over blacklist.
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
    df = pd.DataFrame(get_results())
    df = df[config.DATA_ARTICLES_COLUMNS]
    df.to_csv(config.DATA_ARTICLES_PATH, index=False)
    if url_id_blacklist:
        print(f'Unnecessary IDs in articles blacklist: {", ".join(url_id_blacklist)}')


if __name__ == '__main__':
    main()

# TODO: Use config articles whitelist.
