import logging
import math
import time
from typing import Iterable, List, Set, Tuple, Union

import arxiv
import pandas as pd

from arxivmlrev import config
from arxivmlrev.util.resource import humanized_rss, resident_set_size
from arxivmlrev.util.string import readable_list
from arxivmlrev.util.time import verbose_sleep
from arxivmlrev.result import Result

log = logging.getLogger(__name__)


class Searcher:

    # Ref: https://arxiv.org/help/api/user-manual

    class QueryTypeInvalid(Exception):
        pass

    class ArxivResultsInsufficient(Exception):
        pass

    def __init__(self, *, max_results: Union[int, float] = math.inf):
        self._title_query = self._form_title_query()
        self._max_results = max_results
        self._sort_by = 'lastUpdatedDate' if math.isfinite(self._max_results) else 'submittedDate'
        # Note: Using lastUpdatedDate as the sort order when max_results is inf prevents the oldest 80 or so results
        # from being returned. This condition is prevented above by then using submittedDate as the sort order.

        self._max_results_per_query = int(min(config.MAX_RESULTS_PER_QUERY,
                                              self._max_results * math.e  # This allows ample room for filtering.
                                              ))
        self._rss_start = resident_set_size()
        self._log_state()

    @staticmethod
    def _filter_results(results: List[dict]) -> Iterable[dict]:
        log.debug('Processing %s results.', len(results))
        num_yielded = 0
        try:
            for result_dict in results:
                result = Result(result_dict)
                if (not result.is_id_whitelisted) and (result.is_id_blacklisted or (not result.is_title_whitelisted)):
                    # Note: Title whitelist is checked to skip erroneous match, e.g. "tours" for search term "tour".
                    # log.debug('Skipped result: %s (v%s) (%s) (%s)',
                    #           result.title, result.version, result.updated, result.categories_str)
                    continue
                num_yielded += 1
                yield result.to_dict
        finally:
            log.debug('Yielded %s of %s results.', num_yielded, len(results))

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
        log.debug('Title search query (unsubmitted multiline version): %s', query)
        query = query.strip().replace('\n', ' ')
        while '  ' in query:
            query = query.replace('  ', ' ')
        query = query.replace('( ', '(').replace(' )', ')')
        # Note: A sufficiently longer query can very possibly lead to arXiv returning incomplete results.
        # log.debug('Title search query (actual single-line version):\n%s', query)
        log.debug('Title search query length is %s characters.', len(query))
        return query

    def _log_memory(self, level: int = logging.INFO) -> None:
        log.log(level, 'Additional memory used since initialization of searcher is %s. Total memory used is %s.',
                humanized_rss(self._rss_start), humanized_rss())

    def _log_state(self) -> None:
        log.debug('The %s enabled categories are %s.', len(config.CATEGORIES), readable_list(sorted(config.CATEGORIES)))
        log.debug('The number of title search terms whitelisted and blacklisted are %s and %s respectively.',
                  len(config.TERMS_WHITELIST), len(config.TERMS_BLACKLIST))
        log.debug('The number of search IDs whitelisted and blacklisted are %s and %s respectively.',
                  len(config.URL_ID_WHITELIST), len(config.URL_ID_BLACKLIST))
        log.debug('Max results requested is %s.', self._max_results)
        log.debug('Max results per query is set to %s.', self._max_results_per_query)
        self._log_memory(logging.DEBUG)

    def _run_query(self, *, query_type: str, start: int, interval: float) -> Tuple[List[dict], float]:
        for num_query_attempt in range(1, config.MAX_QUERY_ATTEMPTS + 1):
            log.info('Starting %s query at offset %s.', query_type, start)
            if query_type == 'title':
                results = arxiv.query(search_query=self._title_query, start=start,
                                      max_results=self._max_results_per_query, sort_by=self._sort_by)
                min_num_expected_results = self._max_results_per_query if start == 0 else 1
                # Note: If start > 0, there can actually genuinely be 0 results, but the chances of this are too low.
            elif query_type == 'ID':
                results = arxiv.query(id_list=sorted(config.URL_ID_WHITELIST), start=start,
                                      max_results=self._max_results_per_query, sort_by=self._sort_by)
                min_num_expected_results = min(len(config.URL_ID_WHITELIST) - start, self._max_results_per_query)
            else:
                msg = f'The query type "{query_type}" is invalid.'
                log.error(msg)
                raise self.QueryTypeInvalid(msg)
            if len(results) >= min_num_expected_results:
                log.info('The %s query returned %s results which is a sufficient number.', query_type, len(results))
                break
            if num_query_attempt != config.MAX_QUERY_ATTEMPTS:
                log.warning('The %s query returned %s results which is an insufficient number relative to an '
                            'expectation of at least %s. The query will be rerun.',
                            query_type, len(results), min_num_expected_results)
                verbose_sleep(interval)
                interval *= 1.3678794411714423  # 1 + (1/e) == 1.3678794411714423
        else:
            msg = f'Despite multiple attempts, the {query_type} query failed with insufficient results.'
            log.error(msg)
            raise self.ArxivResultsInsufficient(msg)
        return results, interval

    def _run_search(self, *, search_type: str) -> Iterable[dict]:
        max_results = self._max_results
        start = 0
        num_yielded = 0
        interval = max(3., math.log(self._max_results_per_query))
        rss_search_start = resident_set_size()
        self._log_memory()
        while True:
            results, interval = self._run_query(query_type=search_type, start=start, interval=interval)
            query_completion_time = time.monotonic()
            for result in self._filter_results(results):
                num_yielded += 1
                yield result
                if num_yielded == max_results:
                    break  # Will log and "return".

            log.info('Additional memory used since start of %s queries, with %s results yielded, is %s.',
                     search_type, num_yielded, humanized_rss(rss_search_start))
            if (num_yielded >= max_results) or (len(results) < self._max_results_per_query):
                log.info('Completed all %s queries, yielding %s results.', search_type, num_yielded)
                return

            start += self._max_results_per_query
            sleep_time = max(0., interval - (time.monotonic() - query_completion_time))
            verbose_sleep(sleep_time)

    @staticmethod
    def _set_to_query(strset: Set[str], prefix: str) -> str:
        strset = {f'"{s}"' if ' ' in s else s for s in strset}
        strset_ = ' OR '.join(f'{prefix}:{s}' for s in sorted(strset))
        return f'({strset_})'

    def _search(self, *, search_type: str) -> pd.DataFrame:
        results = self._run_search(search_type=search_type)
        df = pd.DataFrame(results)
        df = df[config.DATA_ARTICLES_CSV_COLUMNS]
        return df

    def search(self) -> pd.DataFrame:
        df_results_for_title_search = df_results = self._search(search_type='title')
        if len(df_results) >= self._max_results:
            log.debug('Skipped whitelisted ID search.')
        else:
            df_results_for_id_search = self._search(search_type='ID')

            mask = df_results_for_title_search['URL_ID'].isin(df_results_for_id_search['URL_ID'])
            unnecessary_whitelisted_ids = df_results_for_title_search['URL_ID'][mask]
            mask = ~unnecessary_whitelisted_ids.isin(config.URL_ID_WHITELIST_INTERSECTION_IGNORED)
            unnecessary_whitelisted_ids = unnecessary_whitelisted_ids[mask]
            # Note: df_results_for_title_search doesn't reliably include URL_ID_WHITELIST_INTERSECTION_IGNORED. The
            # reason for this unpredictability is unknown.
            if not unnecessary_whitelisted_ids.empty:
                csv = unnecessary_whitelisted_ids.to_csv(header=False, index=False).rstrip().replace('\n', ', ')
                log.warning('URL ID whitelist has %s unnecessary IDs which are already present in the title search '
                            'results: %s', len(unnecessary_whitelisted_ids), csv)

            df_results = df_results_for_title_search.append(df_results_for_id_search, ignore_index=True)
            df_results.drop_duplicates('URL_ID', inplace=True)  # In case duplicated from ID whitelist.
            log.info('Concatenated %s title and %s ID search results dataframes into a single dataframe with %s '
                     'results.',
                     len(df_results_for_title_search), len(df_results_for_id_search), len(df_results))

        df_results.sort_values(['Updated', 'Published', 'URL_ID'], ascending=False, inplace=True)
        if len(df_results) > self._max_results:
            df_results = df_results.head(self._max_results)
            log.info('Limited search results dataframe to %s results.', len(df_results))
        self._log_memory()
        return df_results
