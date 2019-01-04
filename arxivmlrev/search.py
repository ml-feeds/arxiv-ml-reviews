import logging
import time
from typing import Iterable, List, Set

import arxiv
import pandas as pd

from arxivmlrev import config
from arxivmlrev.util.humanize import humanize_bytes
from arxivmlrev.util.resource import get_resident_set_size
from arxivmlrev.util.string import readable_list
from arxivmlrev.util.time import verbose_sleep
from arxivmlrev.result import Result

log = logging.getLogger(__name__)


class Searcher:

    class ArxivResultsInsufficient(Exception):
        pass

    def __init__(self):
        self._log_state()
        self._query = self._form_query()
        self._interval = config.MIN_INTERVAL_BETWEEN_QUERIES

    @staticmethod
    def _filter_results(results: List[dict]) -> Iterable[dict]:
        log.info('Filtering %s results.', len(results))
        for result in results:
            result = Result(result)
            if (not result.is_id_whitelisted) and (result.is_id_blacklisted or (not result.is_title_whitelisted)):
                # Note: Title whitelist is checked to skip erroneous match, e.g. "tours" for search term "tour".
                continue
            yield result.to_dict
        log.info('Completed filtering results.')

    @property
    def _form_query(self) -> str:
        title_whitelist_query = self._set_to_query(config.TERMS_WHITELIST, 'ti')
        title_blacklist_query = self._set_to_query(config.TERMS_BLACKLIST, 'ti')
        id_whitelist_query = self._set_to_query(config.URL_ID_WHITELIST, 'id')
        # Note: Specifying a long ID blacklist clause causes the query to return no results, and so this check is local.
        category_query = self._set_to_query(config.CATEGORIES, 'cat')
        # Note: Title blacklist has precedence over title whitelist in the query below.
        query = f'''
            (
                {category_query}
                AND {title_whitelist_query}
                ANDNOT {title_blacklist_query}
            )
            OR {id_whitelist_query}
        '''
        log.info('Search query (multiline version): %s', self._query)
        return query.replace('\n', ' ')

    @staticmethod
    def _log_state():
        log.info('The %s enabled categories are: %s', len(config.CATEGORIES), readable_list(sorted(config.CATEGORIES)))
        log.info('The number of terms whitelisted and blacklisted are %s and %s respectively.',
                 len(config.TERMS_WHITELIST), len(config.TERMS_BLACKLIST))
        log.info('The number of IDs whitelisted and blacklisted are %s and %s respectively.',
                 len(config.URL_ID_WHITELIST), len(config.URL_ID_BLACKLIST))
        log.info('Max results per query is %s.', config.MAX_RESULTS_PER_QUERY)

    def _run_query(self, start: int) -> List[dict]:
        for attempt in range(3):
            log.info('Starting query at offset %s.', start)
            results = arxiv.query(search_query=self._query, start=start,
                                  max_results=config.MAX_RESULTS_PER_QUERY, sort_by='submittedDate')
            min_num_expected_results = config.MAX_RESULTS_PER_QUERY if start == 0 else 1
            # Note: If start > 0, there can actually genuinely be 0 results, but the chances of this are too low.
            if len(results) >= min_num_expected_results:
                log.info('Query returned sufficient (%s) results.', len(results))
                break
            log.warning('Query returned insufficient (%s) results with an expectation of at least %s. '
                        'It will be rerun.', len(results), min_num_expected_results)
            verbose_sleep(self._interval)
            self._interval *= 1.3678794411714423  # 1 + (1/e) == 1.3678794411714423
        else:
            msg = 'Despite multiple attempts, query failed with insufficient results.'
            log.error(msg)
            raise self.ArxivResultsInsufficient(msg)
        return results

    def _run_search(self) -> Iterable[Result]:
        start = 0
        rss_start = get_resident_set_size()
        log.info('Memory used before query is %s.', humanize_bytes(rss_start))
        while True:
            results = self._run_query(start)
            query_completion_time = time.time()
            yield from self._filter_results(results)

            rss_excess = humanize_bytes(get_resident_set_size() - rss_start)
            log.info('Additional memory used since first query is %s.', rss_excess)
            if len(results) < config.MAX_RESULTS_PER_QUERY:
                log.info('Completed all queries.')
                return
            start += config.MAX_RESULTS_PER_QUERY
            sleep_time = max(0, self._interval - (time.time() - query_completion_time))
            verbose_sleep(sleep_time)

    @staticmethod
    def _set_to_query(strset: Set[str], prefix: str) -> str:
        strset = {f'"{s}"' if ' ' in s else s for s in strset}
        strset = ' OR '.join(f'{prefix}:{s}' for s in sorted(strset))
        return f'({strset})'

    def search(self) -> pd.DataFrame:
        results = self._run_search()
        df = pd.DataFrame(results)
        df = df[config.DATA_ARTICLES_CSV_COLUMNS]
        return df
