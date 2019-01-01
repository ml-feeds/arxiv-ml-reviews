from github import Github

from arxivmlrev import config

_GITHUB_ACCESS_TOKEN = config.GITHUB_ACCESS_TOKEN_PATH.read_text().strip()

github = Github(_GITHUB_ACCESS_TOKEN)
repo = github.get_repo(config.GITHUB_PUBLISH_REPO)
content_new = config.DATA_ARTICLES_MD_PATH.read_text()

try:
    contents = repo.get_contents(config.GITHUB_MD_PUBLISH_PATH)
except github.GithubException.UnknownObjectException:
    print('Creating file.')
    repo.create_file(path=config.GITHUB_MD_PUBLISH_PATH, message='Publish reviews', content=content_new)
else:
    if contents.decoded_content.decode() != content_new:
        print('Updating file.')
        repo.update_file(path=config.GITHUB_MD_PUBLISH_PATH, message='Refresh reviews', content=content_new,
                         sha=contents.sha)
    else:
        print('Skipping file update.')
