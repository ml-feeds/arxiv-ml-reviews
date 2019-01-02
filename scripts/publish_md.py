import logging

from github import Github

from arxivmlrev import config

log = logging.getLogger(__name__)

_GITHUB_ACCESS_TOKEN = config.GITHUB_ACCESS_TOKEN_PATH.read_text().strip()
log.info('GitHub access token was read.')
log.info('The target GitHub repo is "%s" and file path is "%s".',
         config.GITHUB_PUBLISH_REPO, config.GITHUB_MD_PUBLISH_PATH)

github = Github(_GITHUB_ACCESS_TOKEN)
repo = github.get_repo(config.GITHUB_PUBLISH_REPO)
log.info('GitHub access token was validated.')
content_new = config.DATA_ARTICLES_MD_PATH.read_text()

try:
    log.info('Attempting to read existing GitHub file')
    contents = repo.get_contents(config.GITHUB_MD_PUBLISH_PATH)
    log.info('Read existing GitHub file.')
except github.GithubException.UnknownObjectException:
    log.info('Unable to read existing GitHub file.')
    log.info('Creating new GitHub file.')
    repo.create_file(path=config.GITHUB_MD_PUBLISH_PATH, message='Publish reviews', content=content_new)
    log.info('Created new GitHub file.')
else:
    if contents.decoded_content.decode() != content_new:
        log.info('Updating existing GitHub file.')
        repo.update_file(path=config.GITHUB_MD_PUBLISH_PATH, message='Refresh reviews', content=content_new,
                         sha=contents.sha)
        log.info('Updated existing GitHub file.')
    else:
        log.info('Existing GitHub file is already up to date.')
