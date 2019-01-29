from dataclasses import dataclass
from string import punctuation
from typing import Dict, List, Union

from arxivmlrev import config


@dataclass
class Result:
    result: dict

    @property
    def _title_cmp(self) -> str:
        """Return the modified title used for comparison against a whitelist or blacklist."""
        return ''.join(c for c in self.title.lower() if c not in punctuation)

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
    def is_id_blacklisted(self):
        return self.url_id in config.URL_ID_BLACKLIST

    @property
    def is_id_whitelisted(self):
        return self.url_id in config.URL_ID_WHITELIST

    @property
    def is_title_whitelisted(self):
        """Return whether the title has one or more terms that are whitelisted."""
        return any(f' {term} ' in f' {self._title_cmp} ' for term in config.TERMS_WHITELIST)

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
        return self.result['arxiv_url'].replace('http://arxiv.org/abs/', '', 1)

    @property
    def version(self) -> str:
        return self.url_id_versioned.rsplit('v', 1)[1]

    @property
    def published(self) -> int:
        return self.result['published_parsed']

    @property
    def updated(self) -> int:
        return self.result['updated_parsed']

    @property
    def published_year(self) -> int:
        return self.published.tm_year

    @property
    def updated_year(self) -> int:
        return self.updated.tm_year

    @property
    def to_dict(self) -> Dict[str, Union[str, int]]:
        assert self.categories_str.startswith(self.category)
        return {'URL_ID': self.url_id, 'Version': self.version,
                'Category': self.category, 'Categories': self.categories_str,
                'Title': self.title, 'Abstract': self.abstract,
                'Published': self.published, 'Updated': self.updated,
                'Year_Published': self.published_year, 'Year_Updated': self.updated_year,
                }
