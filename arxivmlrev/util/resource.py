from pathlib import Path
from resource import getpagesize

_PAGESIZE = getpagesize()
_PATH = Path('/proc/self/statm')


def get_resident_set_size() -> int:
    """Return the current resident set size in bytes."""
    # Ref: https://stackoverflow.com/a/53486808/
    # statm columns are: size resident shared text lib data dt
    statm = _PATH.read_text()
    fields = statm.split()
    return int(fields[1]) * _PAGESIZE
