from pathlib import Path
from resource import getpagesize

from arxivmlrev.util.humanize import humanize_bytes


_PAGESIZE = getpagesize()
_PATH = Path('/proc/self/statm')


def _resident_set_size() -> int:
    """Return the current resident set size in bytes."""
    # Ref: https://stackoverflow.com/a/53486808/
    # statm columns are: size resident shared text lib data dt
    statm = _PATH.read_text()
    fields = statm.split()
    return int(fields[1]) * _PAGESIZE


def resident_set_size(subtract: int = 0) -> int:
    return _resident_set_size() - subtract


def humanized_rss(subtract: int = 0) -> str:
    return humanize_bytes(resident_set_size(subtract))
