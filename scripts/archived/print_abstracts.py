import arxiv
import pandas as pd

from arxivmlrev.result import Result

ARTICLES = """
URL_ID,Category,Title,Year_Published,Year_Updated
1812.01259,eess.IV,"Camera Based Optical Communications, Localization, Navigation, and Motion Capture: A Survey",2018,2018
1812.01780,eess.AS,Feature Extraction for Temporal Signal Recognition: An Overview,2018,2018
"""  # Update list as needed, e.g. using:  git diff -U0 -- data/articles.csv | grep ^+ | sed s/+//

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
