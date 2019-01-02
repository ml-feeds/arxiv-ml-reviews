from humanize import naturalsize


def humanize_bytes(num_bytes: int) -> str:
    return naturalsize(num_bytes, binary=True, format='%.0f')
