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
    def __init__(self) -> None:
        self._searcher = Searcher(max_results=config.FEED_NUM_ITEMS)

    @staticmethod
    def _init_feed() -> FeedGenerator:
        feed = FeedGenerator()
        feed.title(config.FEED_TITLE)
        feed.link(href=config.REPO_URL, rel='self')
        feed.description(config.FEED_DESCRIPTION)
        return feed

    def _output(self, results: pd.DataFrame) -> bytes:
        feed = self._init_feed()
        for _, result in results.iterrows():
            entry = feed.add_entry(order='append')

            # Add title
            primary_category = result.Categories.split(', ', 1)[0]
            years = result.Published.year if (result.Published.year == result.Updated.year) else \
                f'{result.Published.year}-{result.Updated.year}'
            title = f'{result.Title} ({years}) ({primary_category})'
            entry.title(title)

            # Add link
            link = versioned_url_id_to_url(result.URL_ID, result.Version)
            entry.link(href=link)
            entry.guid(link, permalink=True)

            entry.description(result.Abstract)
            entry.published(result.Updated)  # Intentionally not result.Published.
            for category in result.Categories.split(', '):
                entry.category(term=category)
            log.debug('Added: %s (%s)', title, result.Updated)

        text_: bytes = feed.rss_str(pretty=True)
        return text_

    @ttl_cache(maxsize=1, ttl=config.FEED_CACHE_TTL)
    def feed(self) -> bytes:
        log.info('Requesting %s results.', config.FEED_NUM_ITEMS)
        results = self._searcher.search()
        log.debug('Received %s results.', len(results))
        text = self._output(results)
        log.info('XML output has %s items and size %s.', text.count(b'<item>'), humanize_len(text))
        return text


def humanize_len(text: bytes) -> str:
    return naturalsize(len(text), gnu=True, format='%.0f')
