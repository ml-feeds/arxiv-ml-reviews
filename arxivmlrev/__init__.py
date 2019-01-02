import logging.config

from arxivmlrev.config import LOGGING_CONF_PATH

logging.config.fileConfig(LOGGING_CONF_PATH)
logging.getLogger(__name__).info('Logging is configured.')
