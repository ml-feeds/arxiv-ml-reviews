from dataclasses import dataclass
import datetime
from string import punctuation
from typing import Any, Dict, List

from dateutil.parser import parse as dateutil_parse

from arxivmlrev import config

_URL_BASE = 'http://arxiv.org/abs/'


@dataclass
class Result:
    result: dict

    @property
    def abstract(self) -> str:
        return self.abstract_multiline.replace('\n', ' ')

    @property
    def abstract_multiline(self) -> str:
        """Return a multiline abstract."""
        return self.result['summary']

    @property
    def categories(self) -> List[str]:
        categories = [tag['term'] for tag in self.result['tags']]
        categories = [c for c in categories if ' ' not in c]  # Example of invalid category: 'A.1; I.2.7'
        categories.sort()

        # Ensure primary category is first
        primary = self.category
        try:
            categories.remove(primary)
        except ValueError:
            pass
        categories.insert(0, primary)

        return categories

    @property
    def categories_str(self) -> str:
        return ', '.join(self.categories)

    @property
    def category(self) -> str:
        """Return the primary category."""
        return self.result['arxiv_primary_category']['term']

    @property
    def is_id_blacklisted(self) -> bool:
        return self.url_id in config.URL_ID_BLACKLIST

    @property
    def is_id_whitelisted(self) -> bool:
        return self.url_id in config.URL_ID_WHITELIST

    @property
    def is_title_blacklisted(self) -> bool:
        """Return whether the title matches the regular expression of the blacklisted terms."""
        return bool(config.TERMS_BLACKLIST_REGEX.search(self.title))

    @property
    def is_title_whitelisted(self) -> bool:
        """Return whether the title matches any of the regular expressions of the whitelisted terms."""
        title = self.title
        regexes = config.TERMS_WHITELIST_REGEXES
        return bool(any(regex.search(title) for regex in regexes))

    @property
    def title(self) -> str:
        return self.result['title'].replace('\n ', '')

    @property
    def url_id(self) -> str:
        """Return the unique version-agnostic URL ID.

        Unlike `self.result['id']`, this version-agnostic URL ID is actually unique, especially for results older than
        2007.
        """
        return self.url_id_versioned.rsplit('v', 1)[0]

    @property
    def url_id_versioned(self) -> str:
        """Return the unique versioned URL ID.

        Unlike `self.result['id']`, this versioned URL ID is actually unique, especially for results older than 2007.
        """
        return self.result['arxiv_url'].replace(_URL_BASE, '', 1)

    @property
    def version(self) -> int:
        return int(self.url_id_versioned.rsplit('v', 1)[1])

    @property
    def published(self) -> datetime.datetime:
        return dateutil_parse(self.result['published'])  # tz aware

    @property
    def updated(self) -> datetime.datetime:
        return dateutil_parse(self.result['updated'])  # tz aware

    @property
    def published_year(self) -> int:
        return self.published.year

    @property
    def updated_year(self) -> int:
        return self.updated.year

    @property
    def to_dict(self) -> Dict[str, Any]:
        return {'URL_ID': self.url_id, 'Version': self.version, 'Published': self.published, 'Updated': self.updated,
                'Title': self.title, 'Categories': self.categories_str, 'Abstract': self.abstract}


def versioned_url_id_to_url(url_id: str, version: int) -> str:
    return f'{_URL_BASE}{url_id}v{version}'
