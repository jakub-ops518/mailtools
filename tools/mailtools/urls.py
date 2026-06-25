import re
from .utils import unique_keep_order
URL_RE = re.compile(r'https?://[^\s\"\'<>()]+', re.I)


def extract_urls(msg):
    urls = []
    for part in msg.walk():
        if part.get_content_type() not in ('text/plain', 'text/html'):
            continue
        try:
            payload = part.get_content()
        except Exception:
            continue
        if payload:
            urls.extend(URL_RE.findall(str(payload)))
    return unique_keep_order([url.rstrip('.,;)]}>\"\'') for url in urls])
