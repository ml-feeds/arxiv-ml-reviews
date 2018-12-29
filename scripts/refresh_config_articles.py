import arxiv

from arxivmlrev import config
from arxivmlrev.result import Result

df = config.CONFIG_ARTICLES.copy()
url_ids = df['URL_ID'].tolist()
assert 0 < len(url_ids) <= 2000
results = arxiv.query(id_list=url_ids, max_results=len(url_ids), sort_by='submittedDate')
assert len(results) == len(url_ids)

for result in results:
    result = Result(result)
    df.loc[df.URL_ID == result.url_id, ['Category', 'Title']] = result.category, result.title

df = df.sort_values(['Presence', 'URL_ID'], ascending=False).drop_duplicates('URL_ID')
if not df.equals(config.CONFIG_ARTICLES):
    df.to_csv(config.CONFIG_ARTICLES_PATH, index=False)
