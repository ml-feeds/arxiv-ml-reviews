from datetime import date
import logging
from typing import Optional

from github import Github
import pandas as pd

from arxivmlrev import config
from arxivmlrev.util.string import readable_list

log = logging.getLogger(__name__)


class Results:
    def __init__(self, df_results: Optional[pd.DataFrame]):
        self._df_results = df_results
        if self._df_results is None:
            self._df_results = pd.read_csv(config.DATA_ARTICLES_CSV_PATH,
                                           # dtype={'URL_ID': str, 'Category': 'category'}
                                           )

    def write(self):
        self._write_csv()
        self._write_md()

    def _write_csv(self) -> None:
        self._df_results.to_csv(config.DATA_ARTICLES_CSV_PATH, index=False)
        log.info('Finished writing CSV file with %s rows.', len(self._df_results))

    def _write_md(self) -> None:
        def _linked_category(cat: str) -> str:
            return f'[{cat}](https://arxiv.org/list/{cat}/recent)'

        categories = readable_list(_linked_category(cat) for cat in sorted(config.CATEGORIES))
        prologue = f"""
        This is a mostly auto-generated list of review articles on machine learning and artificial intelligence that \
        are on [arXiv](https://arxiv.org/). \
        Although some of them were written for a specific technical audience or application, the techniques described \
        are nonetheless generally relevant. \
        The list is sorted reverse chronologically. It was generated on {date.today()}. \
        It includes articles mainly from the arXiv categories {categories}. \
        A rememberable short link to this page is [https://j.mp/ml-reviews](https://j.mp/ml-reviews). \
        The [source code](https://github.com/impredicative/arxiv-ml-reviews) along with \
        [raw data](https://raw.githubusercontent.com/impredicative/arxiv-ml-reviews/master/data/articles.csv) for \
        generating this page are linked. \
        This page is currently not automatically updated.
        """

        with config.DATA_ARTICLES_MD_PATH.open('w') as md:
            md.write(f'# Review articles\n{prologue}\n')
            for _, row in self._df_results.iterrows():
                cat = _linked_category(row.Category)
                years = row.Year_Published if (row.Year_Published == row.Year_Updated) else \
                    f'{row.Year_Published}-{row.Year_Updated}'
                link = f'https://arxiv.org/abs/{row.URL_ID}'
                md.write(f'* [{row.Title} ({years})]({link}) ({cat})\n')
        log.info('Finished writing markdown file with %s entries.', len(self._df_results))

    @staticmethod
    def publish_md() -> None:
        log.info('The currently existing markdown file will conditionally be published to GitHub.')
        github_token = config.GITHUB_ACCESS_TOKEN_PATH.read_text().strip()
        log.info('GitHub access token was read.')
        log.info('The target GitHub repo is "%s" and markdown file path is "%s".',
                 config.GITHUB_PUBLISH_REPO, config.GITHUB_MD_PUBLISH_PATH)

        github = Github(github_token)
        repo = github.get_repo(config.GITHUB_PUBLISH_REPO)
        log.info('GitHub access token was validated.')
        content_new = config.DATA_ARTICLES_MD_PATH.read_text()

        try:
            log.info('Attempting to read existing markdown file on GitHub.')
            contents = repo.get_contents(config.GITHUB_MD_PUBLISH_PATH)
            log.info('Read existing GitHub file.')
        except github.GithubException.UnknownObjectException:
            log.info('Unable to read existing markdown file on GitHub.')
            log.info('Creating new markdown file on GitHub.')
            repo.create_file(path=config.GITHUB_MD_PUBLISH_PATH, message='Publish reviews', content=content_new)
            log.info('Created new GitHub markdown file on GitHub.')
        else:
            if contents.decoded_content.decode() != content_new:
                log.info('Updating existing markdown file on GitHub.')
                repo.update_file(path=config.GITHUB_MD_PUBLISH_PATH, message='Refresh reviews', content=content_new,
                                 sha=contents.sha)
                log.info('Updated existing markdown file on GitHub.')
            else:
                log.info('Existing markdown file on GitHub is already up to date.')
