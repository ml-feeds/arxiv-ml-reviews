import logging

import pandas as pd

from arxivmlrev import config
from arxivmlrev.results import Results
from arxivmlrev.search import Searcher

log = logging.getLogger(__name__)


def main():
    df_results_old = pd.read_csv(config.DATA_ARTICLES_CSV_PATH)
    log.info('Preexisting CSV data file has %s rows.', len(df_results_old))
    df_results_new = Searcher().search()
    num_increase = len(df_results_new) - len(df_results_old)
    log.info('Updated dataframe has %s rows. This is a difference of %+d rows since the last update.',
             len(df_results_new), num_increase)
    results = Results(df_results_new)
    results.write()
    log.info('Any newly written data files can be checked into the remote repository.')
    if num_increase > 0:
        Results.publish_md()
    else:
        msg = 'Considering the difference in the number of rows is not positive, the updated markdown file is not ' \
              'being published to GitHub.'
        log.info(msg)

# TODO: Using Fire, create CLI to individually do: run full refresh, just publish md.


if __name__ == '__main__':
    main()
