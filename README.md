# arxiv-ml-reviews
This uses a [keyword](arxivmlrev/_config/terms.csv)-based search to extract a list of review articles from
[arXiv's](https://arxiv.org/) various [categories](arxivmlrev/_config/categories.txt)
on machine learning and artificial intelligence.

The code is admittedly research-grade; it is currently not polished for general use.

## Requirements
* Python 3.7+
* In a new virtual environment or container, run the following, falling back to the versioned `requirements.txt` instead
if there are any issues.
```
pip install -U pip
pip install -r requirements.in
```

## Usage
### full-refresh
Running `python -m arxivmlrev full-refresh --publish=False` will:
1. Rerun the full search and write the results to `data/articles.csv` and `data/articles.md`.
2. If the `data/results.csv` file increased in its number of rows, the command will publish the written markdown file
to GitHub per the GitHub-specific configuration in `config.py`. To enable this step, run the command without
`--publish=False`.

Use git to check if the diff of this updated CSV file looks acceptable.
If the CSV file is smaller for any reason, it means the search query failed, in which case it should be rerun.
**As a warning, this command should not be run excessively** as it burdens the arXiv search server.

If there is any extraneous new entry in `data/articles.csv`, update either `arxivmlrev/_config/articles.csv` and/or
`arxivmlrev/_config/terms.csv` with a new blacklist entry. This is expected to be be done rarely.
Blacklisted entries are those with *Presence* = 0.
Before committing these updated configuration files to revision control, consider running
`scripts/sort_config_articles.py` and/or `scripts/sort_config_terms.py` respectively.
If a configuration file was updated, rerun the command.

### write-md
Running `python -m arxivmlrev write-md` will only refresh the markdown file `data/articles.md` from `data/articles.csv`.

### publish-md
Running `python -m arxivmlrev publish-md` will only publish the markdown file `data/articles.md` to GitHub.
This requires GitHub-specific configuration in `config.py`.

## To do
* By default, run an incremental update, and provide an option to do a full rerun.
An incremental update assumes an unchanged configuration.
This also require changing the code to sort the results by *lastUpdatedDate* rather than by *submittedDate*.
