import arxiv
import pandas as pd

ARTICLES = """
URL_ID,Category,Title
1812.08577,cs.CV,Computational Anatomy for Multi-Organ Analysis in Medical Imaging: A Review
1806.06876,cs.CV,Diving Deep onto Discriminative Ensemble of Histological Hashing & Class-Specific Manifold Learning for Multi-class Breast Carcinoma Taxonomy
"""  # Update list as needed.

df = pd.read_csv(pd.compat.StringIO(ARTICLES), dtype={'URL_ID': str, 'Category': 'category'})
url_ids = df['URL_ID'].tolist()
results = arxiv.query(id_list=url_ids, max_results=len(df), sort_by='submittedDate')
assert len(results) == len(df)
for (index, row), result in zip(df.iterrows(), results):
    url_id = result['arxiv_url'].replace('http://arxiv.org/abs/', '', 1).rsplit('v', 1)[0]
    assert url_id == row.URL_ID
    row_str = pd.DataFrame(row).T.to_csv(header=False, index=False, line_terminator='')
    categories = sorted(d['term'] for d in result['tags'])
    categories_str = ', '.join(categories)
    abstract = result['summary']
    print(f'{row_str}\n{categories_str}\n\t{abstract}\n')
