import logging
import time
from typing import Union

log = logging.getLogger(__name__)


def verbose_sleep(seconds: Union[int, float]) -> None:
    log.info(f'Sleeping for {seconds:.1f}s')
    time.sleep(seconds)
