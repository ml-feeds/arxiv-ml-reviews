import logging

from arxivmlrev import config

log = logging.getLogger(__name__)

df = config.CONFIG_TERMS.copy()
df = df.sort_values(['Presence', 'Term'], ascending=[0, 1]).drop_duplicates('Term')
if not df.equals(config.CONFIG_TERMS):
    df.to_csv(config.CONFIG_TERMS_PATH, index=False)
    log.info('Updated the config terms file.')
else:
    log.info('The config terms file is already sorted.')
