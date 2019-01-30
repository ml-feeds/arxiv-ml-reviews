import logging

from cachetools.func import ttl_cache
from feedgen.feed import FeedGenerator
from humanize import naturalsize
import pandas as pd

from arxivmlrev import config
from arxivmlrev.result import versioned_url_id_to_url
from arxivmlrev.search import Searcher

log = logging.getLogger(__name__)


class Feed:
    def __init__(self):
        self._feed = FeedGenerator()
        self._init_feed()
        self._searcher = Searcher(max_results=config.FEED_NUM_ITEMS)

    def _output(self, results: pd.DataFrame) -> bytes:
        feed = self._feed
        for _, result in results.iterrows():
            entry = feed.add_entry(order='append')
            entry.title(result.Title)
            link = versioned_url_id_to_url(result.URL_ID, result.Version)
            entry.link(href=link)
            entry.guid(link, permalink=True)
            entry.description(result.Abstract)
            entry.published(result.Updated)  # Intentionally not result.Published.
            log.debug('Added: %s (%s)', result.Title, result.Updated)

        text_: bytes = feed.rss_str(pretty=True)
        log.info('XML output has %s items.', text_.count(b'<item>'))
        return text_

    def _init_feed(self) -> None:
        feed = self._feed
        feed.title(config.FEED_TITLE)
        feed.link(href=config.FEED_SOURCE_URL, rel='self')
        feed.description(config.FEED_DESCRIPTION)

    @ttl_cache(maxsize=1, ttl=config.FEED_CACHE_TTL)
    def feed(self) -> bytes:
        log.info('Requesting %s results.', config.FEED_NUM_ITEMS)
        results = self._searcher.search()
        log.info('Received %s results.', len(results))
        text = self._output(results)
        log.info('XML output has size %s.', humanize_len(text))
        return text


def humanize_len(text: bytes) -> str:
    return naturalsize(len(text), gnu=True, format='%.0f')
