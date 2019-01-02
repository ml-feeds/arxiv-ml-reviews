import logging
import time
from typing import Set, Union

import arxiv
from humanize import naturalsize
import pandas as pd

from arxivmlrev import config
from arxivmlrev.util.resource import get_resident_set_size
from arxivmlrev.util.string import readable_list
from arxivmlrev.result import Result

log = logging.getLogger(__name__)
log.info('The %s enabled categories are: %s', len(config.CATEGORIES), readable_list(sorted(config.CATEGORIES)))
log.info('The number of terms whitelisted and blacklisted are %s and %s respectively.',
         len(config.TERMS_WHITELIST), len(config.TERMS_BLACKLIST))
log.info('The number of IDs whitelisted and blacklisted are %s and %s respectively.',
         len(config.URL_ID_WHITELIST), len(config.URL_ID_BLACKLIST))

url_id_blacklist = config.URL_ID_BLACKLIST.copy()


def verbose_sleep(seconds: Union[int, float]) -> None:
    log.info(f'Sleeping for {seconds:.1f}s')
    time.sleep(seconds)


class ArxivResultsInsufficient(Exception):
    pass


def _set_query(strset: Set[str], prefix: str) -> str:
    strset = {f'"{s}"' if ' ' in s else s for s in strset}
    strset = ' OR '.join(f'{prefix}:{s}' for s in sorted(strset))
    return f'({strset})'


def _get_results():
    title_whitelist_query = _set_query(config.TERMS_WHITELIST, 'ti')
    title_blacklist_query = _set_query(config.TERMS_BLACKLIST, 'ti')
    id_whitelist_query = _set_query(config.URL_ID_WHITELIST, 'id')
    # Note: Specifying a long ID blacklist clause causes the query to return no results, and so this check is local.
    category_query = _set_query(config.CATEGORIES, 'cat')
    # Note: Title blacklist has precedence over title whitelist in the query below.
    search_query = f'''
        (
            {category_query}
            AND {title_whitelist_query}
            ANDNOT {title_blacklist_query}
        )
        OR {id_whitelist_query}
    '''
    log.info('Search query: %s', search_query)
    log.info('Max results per query is %s.', config.MAX_RESULTS_PER_QUERY)
    search_query = search_query.replace('\n', ' ')

    interval = config.MIN_INTERVAL_BETWEEN_QUERIES
    start = 0
    rss_start = get_resident_set_size()
    log.info('Memory used before query is %s.', naturalsize(rss_start))
    while True:
        for attempt in range(3):
            log.info('Starting query with start=%s.', start);
            results = arxiv.query(search_query=search_query, start=start, max_results=config.MAX_RESULTS_PER_QUERY,
                                  sort_by='submittedDate')
            query_completion_time = time.time()
            min_num_expected_results = config.MAX_RESULTS_PER_QUERY if start == 0 else 1
            # Note: If start > 0, there can actually genuinely be 0 results, but the chances of this are too low.
            if len(results) >= min_num_expected_results:
                log.info('Query returned sufficient (%s) results.', len(results))
                break
            log.warning('Query returned insufficient (%s) results with an expectation of at least %s. '
                        'It will be rerun.', len(results), min_num_expected_results)
            verbose_sleep(interval)
            interval *= 1.3678794411714423  # 1 + (1/e) == 1.3678794411714423
        else:
            log.error('Despite multiple attempts, query failed with insufficient results.')
            raise ArxivResultsInsufficient

        log.info('Processing %s results.', len(results))
        for result in results:
            result = Result(result)
            if (not result.is_id_whitelisted) and (result.is_id_blacklisted or (not result.is_title_whitelisted)):
                # Note: Title whitelist is checked to skip erroneous match, e.g. "tours" for search term "tour".
                continue
            yield result.to_dict
        log.info('Completed processing results.')

        rss_excess = naturalsize(get_resident_set_size() - rss_start, binary=True)
        log.info('Memory used since first query is %s.', rss_excess)
        if len(results) < config.MAX_RESULTS_PER_QUERY:
            log.info('Completed all queries.')
            return
        start += config.MAX_RESULTS_PER_QUERY
        sleep_time = max(0, interval - (time.time() - query_completion_time))
        verbose_sleep(sleep_time)


def main():
    df = pd.DataFrame(_get_results())
    df = df[config.DATA_ARTICLES_CSV_COLUMNS]
    log.info('Writing CSV.')
    df.to_csv(config.DATA_ARTICLES_CSV_PATH, index=False)


if __name__ == '__main__':
    main()
