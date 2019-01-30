import logging

import arxiv

from arxivmlrev import config
from arxivmlrev.result import Result

log = logging.getLogger(__name__)

df = config.CONFIG_ARTICLES.copy()
url_ids = df['URL_ID'].tolist()
num_url_ids = len(url_ids)
assert 0 < num_url_ids <= 2000

log.info('Querying arXiv for metadata of %s IDs.', num_url_ids)
results = arxiv.query(id_list=url_ids, max_results=num_url_ids, sort_by='submittedDate')
assert len(results) == num_url_ids
log.info('Queried arXiv for metadata of %s IDs.', len(results))

for result in results:
    result = Result(result)
    df.loc[df.URL_ID == result.url_id, 'Title'] = result.title

df = df.sort_values(['Presence', 'URL_ID'], ascending=False).drop_duplicates('URL_ID')
if not df.equals(config.CONFIG_ARTICLES):
    df.to_csv(config.CONFIG_ARTICLES_PATH, index=False)
    log.info('Updated the config articles file.')
else:
    log.info('The config articles file is already up to date.')
