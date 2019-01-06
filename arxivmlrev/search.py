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

    _NUM_QUERY_ATTEMPTS = 3

    # Ref: https://arxiv.org/help/api/user-manual

    class QueryTypeInvalid(Exception):
        pass

    class ArxivResultsInsufficient(Exception):
        pass

    def __init__(self):
        self._log_state()
        self._title_query = self._form_title_query()
        self._interval = config.MIN_INTERVAL_BETWEEN_QUERIES
        self._rss_start = get_resident_set_size()
        log.debug('Memory used is %s.', humanize_bytes(self._rss_start))

    @staticmethod
    def _filter_results(results: List[dict]) -> Iterable[dict]:
        log.debug('Filtering %s results.', len(results))
        for result in results:
            result = Result(result)
            if (not result.is_id_whitelisted) and (result.is_id_blacklisted or (not result.is_title_whitelisted)):
                # Note: Title whitelist is checked to skip erroneous match, e.g. "tours" for search term "tour".
                continue
            yield result.to_dict
        # log.debug('Completed filtering %s results.', len(results))

    def _form_title_query(self) -> str:
        category_query = self._set_to_query(config.CATEGORIES, 'cat')
        title_whitelist_query = self._set_to_query(config.TERMS_WHITELIST, 'ti')
        title_blacklist_query = self._set_to_query(config.TERMS_BLACKLIST, 'ti')
        # Note: Title blacklist has precedence over title whitelist in the query below.
        query = f'''
            {category_query}
            AND {title_whitelist_query}
            ANDNOT {title_blacklist_query}
        '''
        log.info('Title search query (multiline version): %s', query)
        query = query.strip().replace('\n', ' ')
        while '  ' in query:
            query = query.replace('  ', ' ')
        query = query.replace('( ', '(').replace(' )', ')')
        # Note: A sufficiently longer query can very possibly lead to arXiv returning incomplete results.
        log.debug('Title search query (actual single-line version):\n%s', query)
        log.info('Title search query length is %s characters.', len(query))
        return query

    @staticmethod
    def _log_state() -> None:
        log.info('The %s enabled categories are %s.', len(config.CATEGORIES), readable_list(sorted(config.CATEGORIES)))
        log.info('The number of title search terms whitelisted and blacklisted are %s and %s respectively.',
                 len(config.TERMS_WHITELIST), len(config.TERMS_BLACKLIST))
        log.info('The number of search IDs whitelisted and blacklisted are %s and %s respectively.',
                 len(config.URL_ID_WHITELIST), len(config.URL_ID_BLACKLIST))
        log.info('Max results per query is set to %s.', config.MAX_RESULTS_PER_QUERY)
        log.info('Memory used is %s.', humanize_bytes(get_resident_set_size()))

    def _run_query(self, *, query_type: str, start: int) -> List[dict]:
        for attempt in range(self._NUM_QUERY_ATTEMPTS):
            log.info('Starting %s query at offset %s.', query_type, start)
            if query_type == 'title':
                results = arxiv.query(search_query=self._title_query, start=start,
                                      max_results=config.MAX_RESULTS_PER_QUERY, sort_by='submittedDate')
                min_num_expected_results = config.MAX_RESULTS_PER_QUERY if start == 0 else 1
                # Note: If start > 0, there can actually genuinely be 0 results, but the chances of this are too low.
            elif query_type == 'ID':
                results = arxiv.query(id_list=sorted(config.URL_ID_WHITELIST), start=start,
                                      max_results=config.MAX_RESULTS_PER_QUERY, sort_by='submittedDate')
                min_num_expected_results = min(len(config.URL_ID_WHITELIST) - start, config.MAX_RESULTS_PER_QUERY)
            else:
                msg = f'The query type "{query_type}" is invalid.'
                log.error(msg)
                raise self.QueryTypeInvalid(msg)
            if len(results) >= min_num_expected_results:
                log.info('The %s query returned %s results which is a sufficient number.', query_type, len(results))
                break
            log.warning('The %s query returned %s results which is an insufficient number relative to an expectation '
                        'of at least %s. The query will be rerun.',
                        query_type, len(results), min_num_expected_results)
            verbose_sleep(self._interval)
            self._interval *= 1.3678794411714423  # 1 + (1/e) == 1.3678794411714423
        else:
            msg = f'Despite multiple attempts, the {query_type} query failed with insufficient results.'
            log.error(msg)
            raise self.ArxivResultsInsufficient(msg)
        return results

    def _run_search(self, *, search_type: str) -> Iterable[Result]:
        start = 0
        while True:
            results = self._run_query(query_type=search_type, start=start)
            query_completion_time = time.time()
            yield from self._filter_results(results)

            rss_excess = humanize_bytes(get_resident_set_size() - self._rss_start)
            log.info('Additional memory used since first query is %s.', rss_excess)
            if len(results) < config.MAX_RESULTS_PER_QUERY:
                log.info('Completed all %s queries.', search_type)
                return
            start += config.MAX_RESULTS_PER_QUERY
            sleep_time = max(0, self._interval - (time.time() - query_completion_time))
            verbose_sleep(sleep_time)

    @staticmethod
    def _set_to_query(strset: Set[str], prefix: str) -> str:
        strset = {f'"{s}"' if ' ' in s else s for s in strset}
        strset = ' OR '.join(f'{prefix}:{s}' for s in sorted(strset))
        return f'({strset})'

    def _search(self, *, search_type: str) -> pd.DataFrame:
        results = self._run_search(search_type=search_type)
        df = pd.DataFrame(results)
        df = df[config.DATA_ARTICLES_CSV_COLUMNS]
        return df

    def search(self) -> pd.DataFrame:
        df_results_for_title_search = self._search(search_type='title')
        df_results_for_id_search = self._search(search_type='ID')
        return df_results_for_title_search
