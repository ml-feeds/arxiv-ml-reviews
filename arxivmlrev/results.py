from datetime import date
import logging
import os

from github import Github
import pandas as pd

from arxivmlrev import config
from arxivmlrev.feed import Feed
from arxivmlrev.search import Searcher
from arxivmlrev.util.string import readable_list

log = logging.getLogger(__name__)


class Results:
    def __init__(self):
        self._df_results = pd.read_csv(config.DATA_ARTICLES_CSV_PATH, parse_dates=['Published', 'Updated'])

    def _write_csv(self) -> None:
        df = self._df_results[config.DATA_ARTICLES_CSV_COLUMNS]
        df.to_csv(config.DATA_ARTICLES_CSV_PATH, index=False, date_format="%Y-%m-%d")
        log.info('Finished writing CSV file with %s rows.', len(df))

    def refresh(self) -> int:
        """Refresh search results locally."""
        df_results_old = self._df_results
        log.info('Preexisting CSV data file has %s rows.', len(df_results_old))
        df_results_new = self._df_results = Searcher().search()
        num_increase = len(df_results_new) - len(df_results_old)
        logger = log.info if num_increase >= 0 else log.error
        logger('Updated dataframe has %s rows. This is a difference of %+d rows since the last update.',
               len(df_results_new), num_increase)
        self._write_csv()
        self.write_md()
        log.info('Any newly written data files can be checked into the remote repository.')
        return num_increase

    def refresh_and_publish(self) -> None:
        """Refresh search results locally, and conditionally publish them."""
        num_increase = self.refresh()
        if num_increase >= 0:
            self.publish_md()
        else:
            msg = 'Considering the difference in the number of rows is negative, the updated markdown file ' \
                  'is not being published to GitHub.'
            log.error(msg)

    @staticmethod
    def write_feed() -> bytes:
        """Return the XML of a RSS feed of the most recently updated search results."""
        feed = Feed().feed()
        feed_path = config.DATA_DIR / 'feed.xml'
        feed_path.write_bytes(feed)
        log.info('Feed was written to %s.', feed_path)
        return feed

    def write_md(self) -> None:
        """Write the search results to a markdown file locally."""
        def _linked_category(cat: str) -> str:
            return f'[{cat}](https://arxiv.org/list/{cat}/recent)'

        categories = readable_list(_linked_category(cat) for cat in sorted(config.CATEGORIES))
        prologue = f"""
        This is a mostly auto-generated list of review articles on machine learning and artificial intelligence that \
        are on [arXiv](https://arxiv.org/). \
        Although some of them were written for a specific technical audience or application, the techniques described \
        are nonetheless generally relevant. \
        The list is sorted reverse chronologically by the last updated date of the reviews. \
        It was generated on {date.today()}. \
        It includes articles mainly from the arXiv categories {categories}. \
        A rememberable short link to this page is [https://j.mp/lc-ml-reviews](https://j.mp/lc-ml-reviews). \
        The [source code](https://github.com/ml-feeds/arxiv-ml-reviews) along with the \
        [CSV data](https://github.com/ml-feeds/arxiv-ml-reviews/blob/master/data/articles.csv) for \
        generating this page are linked. \
        Any incorrect or missing entries can be reported as an \
        [issue](https://github.com/ml-feeds/arxiv-ml-reviews/issues). \
        This page is currently not automatically updated. \
        An auto-updated [RSS feed](https://us-east1-ml-feeds.cloudfunctions.net/arxiv-ml-reviews) is however available.
        """.strip()

        with config.DATA_ARTICLES_MD_PATH.open('w') as md:
            md.write(f'# Review articles\n{prologue}\n')
            for _, row in self._df_results.iterrows():
                primary_category = row.Categories.split(', ', 1)[0]
                primary_category = _linked_category(primary_category)
                years = row.Published.year if (row.Published.year == row.Updated.year) else \
                    f'{row.Published.year}-{row.Updated.year}'
                link_abs = f'https://arxiv.org/abs/{row.URL_ID}'
                link_pdf = f'https://arxiv.org/pdf/{row.URL_ID}'
                md.write(f'* [{row.Title} ({years})]({link_abs}) │ [pdf]({link_pdf}) │ {primary_category}\n')
        log.info('Finished writing markdown file with %s entries.', len(self._df_results))

    @staticmethod
    def publish_md() -> None:
        """Conditionally publish the markdown file to GitHub."""
        log.info('The currently existing markdown file will conditionally be published to GitHub.')
        github_token = os.environ['GITHUB_ACCESS_TOKEN'].strip()
        log.debug('GitHub access token was read.')
        log.info('The target GitHub repo is "%s" and markdown file path is "%s".',
                 config.GITHUB_PUBLISH_REPO, config.GITHUB_MD_PUBLISH_PATH)

        github = Github(github_token)
        repo = github.get_repo(config.GITHUB_PUBLISH_REPO)
        log.info('GitHub access token was validated.')
        content_new = config.DATA_ARTICLES_MD_PATH.read_text()

        try:
            log.debug('Attempting to read existing markdown file on GitHub.')
            contents = repo.get_contents(path=config.GITHUB_MD_PUBLISH_PATH)
            log.info('Read existing GitHub file.')
        except github.GithubException.UnknownObjectException:
            log.info('Unable to read existing markdown file on GitHub.')
            log.debug('Creating new markdown file on GitHub.')
            repo.create_file(path=config.GITHUB_MD_PUBLISH_PATH, message='Publish reviews', content=content_new)
            log.info('Created new GitHub markdown file on GitHub.')
        else:
            if contents.decoded_content.decode() != content_new:
                log.debug('Updating existing markdown file on GitHub.')
                repo.update_file(path=config.GITHUB_MD_PUBLISH_PATH, message='Refresh reviews', content=content_new,
                                 sha=contents.sha)
                log.info('Updated existing markdown file on GitHub.')
            else:
                log.info('Existing markdown file on GitHub is already up to date.')
