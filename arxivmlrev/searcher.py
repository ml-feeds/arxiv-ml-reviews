from arxivmlrev.config import CATEGORIES, TERMS

from string import punctuation

import arxiv

title_query = ' OR '.join(f'ti:{term}' for term in sorted(TERMS))
cat_query = ' OR '.join(f'cat:{cat}' for cat in sorted(CATEGORIES))
search_query = f'({title_query}) AND ({cat_query})'
print(search_query)
results = arxiv.query(search_query=search_query, max_results=100, sort_by='submittedDate')
for result in results:
    id = result['id'].rsplit('/')[-1].rsplit('v')[0]
    title = result['title'].replace('\n ', '')
    title_terms = set(term.rstrip(punctuation) for term in title.lower().split(' '))
    if not(TERMS & title_terms):
        continue
    year = result['published_parsed'].tm_year
    year_updated = result['updated_parsed'].tm_year
    if year != year_updated:
        year = f'{year}-{year_updated}'
    primary_category = result['arxiv_primary_category']['term']
    if primary_category not in CATEGORIES:
        continue
    print(f'{id} {title} ({year}) ({primary_category})')
print
