import arxiv
import pandas as pd

from arxivmlrev.result import Result

ARTICLES = """
URL_ID,Category,Title
1807.11573,cs.CV,State-of-the-art and gaps for deep learning on limited training data in remote sensing
1810.06339,cs.LG,Deep Reinforcement Learning
1802.01528,cs.LG,The Matrix Calculus You Need For Deep Learning
1806.11484,hep-ex,Deep Learning and its Application to LHC Physics
"""  # Update list as needed.

df_all = pd.read_csv(pd.compat.StringIO(ARTICLES), dtype={'URL_ID': str, 'Category': 'category'})
url_ids = df_all['URL_ID'].tolist()
assert 0 < len(url_ids) <= 2000
results = arxiv.query(id_list=url_ids, max_results=len(url_ids))
# Note: Results are expected to be in same order as url_ids.
assert len(results) == len(url_ids)
for result in results:
    result = Result(result)
    csv = result.to_csv(df_all.columns)
    print(f'{csv}\n{result.categories_str}\n\t{result.abstract_multiline}\n')
