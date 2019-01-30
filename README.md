# arxiv-ml-reviews
**arxiv-ml-reviews** mainly uses a [keyword](arxivmlrev/_config/terms.csv)-based search to extract a list of review
articles from [arXiv's](https://arxiv.org/) various [categories](arxivmlrev/_config/categories.txt)
on machine learning and artificial intelligence.

## Links
* [Project repo](https://github.com/ml-feeds/arxiv-ml-reviews)
* [**HTML list**](https://freenode-machinelearning.github.io/Resources/ArticlesReview.html)
* [**RSS feed**](https://us-east1-ml-feeds.cloudfunctions.net/arxiv-ml-reviews)

## Requirements
* Python 3.7+
* In a new virtual environment or container, run the following, falling back to the versioned `requirements.txt` instead
if there are any issues.
```
pip install -U pip
pip install -r requirements.in
```

## Usage commands
### refresh
Running `python -m arxivmlrev refresh` will rerun the full online search and write the results to `data/articles.csv`
and `data/articles.md`.

Use git to discern whether the diff of this updated CSV file looks acceptable.
If the CSV file is smaller for any reason, it means the search query failed, in which case it should be rerun.
**As a warning, this command should not be run excessively** as it burdens the arXiv search server.

If there is any extraneous new entry in `data/articles.csv`, update either `arxivmlrev/_config/articles.csv` and/or
`arxivmlrev/_config/terms.csv` with a new blacklist entry. This is expected to be be done rarely.
Blacklisted entries are those with *Presence* = 0.
Before committing these updated configuration files to revision control, consider running
`scripts/sort_config_articles.py` and/or `scripts/sort_config_terms.py` respectively.
If a configuration file was updated, rerun the command.
**Be warned that a sufficiently longer query can very possibly lead to arXiv returning incomplete results,** and this
will require a rearchitecture of the search.

### refresh-and-publish
Running `python -m arxivmlrev refresh-and-publish` will refresh and also conditionally publish the results.
Specifically, if the `data/results.csv` file changed but didn't decrease in its number of rows, the command will publish
the written markdown file to GitHub per the GitHub-specific configuration in `config.py`.
In this configuration file, refer to parameters starting with the prefix `GITHUB_`.

### write-feed
Running `python -m arxivmlrev write-feed` will perform an online search to write the XML file `data/feed.xml`.
This file is excluded from git.

### write-md
Running `python -m arxivmlrev write-md` will perform an offline refresh of the markdown file `data/articles.md` from
`data/articles.csv`.

### publish-md
Running `python -m arxivmlrev publish-md` will publish the markdown file `data/articles.md` to GitHub.
This requires GitHub-specific configuration in `config.py`.
In this configuration file, refer to parameters starting with the prefix `GITHUB_`.

## To do
* By default, run an incremental update, and provide an option to do a full rerun.
An incremental update assumes an unchanged configuration.
This requires query results to be sorted by *lastUpdatedDate*.

## Deployment
Serverless deployment of the RSS feed to [Google Cloud Functions](https://console.cloud.google.com/functions/) is
configured.
It requires the the following files:
* requirements.txt
* main.py (having callable `serve(request: flask.Request) -> Tuple[bytes, int, Dict[str, str]]`)

Deployment version updates are not automated.
They can be performed manually by editing and saving the function configuration.

These deployment links require access:
* [Dashboard](https://console.cloud.google.com/functions/details/us-east1/arxiv-ml-reviews?project=ml-feeds)
* [Logs](https://console.cloud.google.com/logs?service=cloudfunctions.googleapis.com&key1=arxiv-ml-reviews&key2=us-east1&project=ml-feeds)
* [Repo](https://source.cloud.google.com/ml-feeds/github_ml-feeds_arxiv-ml-reviews)
