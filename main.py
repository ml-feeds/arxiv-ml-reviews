import logging
from typing import Dict, Tuple

import flask

from arxivmlrev.feed import Feed

log = logging.getLogger(__name__)
feed = Feed()


def serve(request: flask.Request) -> Tuple[bytes, int, Dict[str, str]]:
    hget = request.headers.get
    log.info('Received request from %s from %s, %s, %s.', hget('X-Appengine-User-Ip'),
             hget('X-Appengine-City'), hget('X-Appengine-Region'), hget('X-Appengine-Country'))
    return feed.feed(), 200, {'Content-Type': 'text/xml; charset=utf-8'}
