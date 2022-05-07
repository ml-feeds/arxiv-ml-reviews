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
                if not result.is_id_whitelisted:
                    if result.is_id_blacklisted or result.title_blacklist_match or (not result.title_whitelist_match):
                        # log.debug('Skipped result: %s (v%s) (%s) (%s)',
                        #           result.title, result.version, result.updated, result.categories_str)
                        continue
                num_yielded += 1
                yield result.to_dict
        finally:
            log.debug('Yielded %s of %s results.', num_yielded, len(results))

    def _form_title_query(self) -> str:
        category_query = self._list_to_query(config.CATEGORIES, 'cat')
        title_whitelist_query = self._list_to_query(config.TERMS_WHITELIST, 'ti')
        title_blacklist_query = self._list_to_query(config.TERMS_BLACKLIST, 'ti')
        # Note: Title blacklist has precedence over title whitelist in the query below.
        query = f'''
            {category_query}
            AND {title_whitelist_query}
            ANDNOT {title_blacklist_query}
        '''.strip('\n')
        log.debug('Title search query (unsubmitted multiline version):\n%s', query)
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
        # log.debug('The %s whitelisted regexes are:\n• %s', len(config.TERMS_WHITELIST_REGEXES),
        #           '\n• '.join(regex.pattern for regex in config.TERMS_WHITELIST_REGEXES))
        # log.debug('The blacklisted regex is:\n%s', config.TERMS_BLACKLIST_REGEX.pattern)
        log.debug('The number of search IDs whitelisted and blacklisted are %s and %s respectively.',
                  len(config.URL_ID_WHITELIST), len(config.URL_ID_BLACKLIST))
        log.debug('Max results requested is %s.', self._max_results)
        log.debug('Max results per query is set to %s.', self._max_results_per_query)
        self._log_memory(logging.DEBUG)

    def _run_query(self, *, query_type: str, start: int) -> List[dict]:
        log.info('Starting %s query at offset %s.', query_type, start)
        if query_type == 'title':
            results = arxiv.query(query=self._title_query, start=start,
                                  max_results=self._max_results_per_query, sort_by=self._sort_by)
        elif query_type == 'ID':
            if config.URL_ID_WHITELIST:
                results = arxiv.query(id_list=sorted(config.URL_ID_WHITELIST), start=start,
                                      max_results=self._max_results_per_query, sort_by=self._sort_by)
            else:
                results = []
        else:
            msg = f'The query type "{query_type}" is invalid.'
            log.error(msg)
            raise self.QueryTypeInvalid(msg)
        log.info('The %s query at offset %s returned %s results.', query_type, start, len(results))
        return results

    def _run_search(self, *, search_type: str) -> Iterable[dict]:
        max_results = self._max_results
        start, num_yielded, num_successive_empty_results = 0, 0, 0
        rss_search_start = resident_set_size()
        self._log_memory()
        while True:
            results = self._run_query(query_type=search_type, start=start)
            query_completion_time = time.monotonic()
            num_successive_empty_results = 0 if results else (num_successive_empty_results + 1)
            for result in self._filter_results(results):
                num_yielded += 1
                yield result
                if num_yielded == max_results:
                    break

            log.info('Additional memory used since start of %s queries, with %s results yielded, is %s.',
                     search_type, num_yielded, humanized_rss(rss_search_start))
            if (num_yielded >= max_results) or (num_successive_empty_results >= 3):
                log.info('Completed all %s queries, yielding %s results.', search_type, num_yielded)
                return
            start += len(results)

            sleep_time = max(0., config.QUERY_INTERVAL - (time.monotonic() - query_completion_time))
            verbose_sleep(sleep_time)

    @staticmethod
    def _list_to_query(params: List[str], prefix: str) -> str:
        assert params == sorted(set(p.strip() for p in params))
        params = [f'"{s}"' if ' ' in s else s for s in params]
        query = ' OR '.join(f'{prefix}:{s}' for s in params)
        return f'({query})'

    def _search(self, *, search_type: str) -> pd.DataFrame:
        columns = config.DATA_ARTICLES_COLUMNS
        results = self._run_search(search_type=search_type)
        df = pd.DataFrame(results)
        return pd.DataFrame(columns=columns) if df.empty else df[columns]

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

            df_results = pd.concat([df_results_for_title_search, df_results_for_id_search], ignore_index=True)
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
