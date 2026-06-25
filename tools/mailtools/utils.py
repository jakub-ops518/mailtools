import ipaddress
from datetime import timezone
from email.utils import parsedate_to_datetime

LINE = '-' * 64


def clean_header(value):
    return ' '.join(str(value).split()) if value else '-'


def clean_host(value):
    return value.strip().strip('<>[](),;')


def unique_keep_order(values):
    result = []
    seen = set()
    for value in values:
        if not value:
            continue
        key = str(value).lower()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def is_public_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_global
    except ValueError:
        return False


def ip_type(ip):
    if not ip or ip == '-':
        return '-'
    try:
        obj = ipaddress.ip_address(ip)
        if obj.is_global:
            return 'public'
        if obj.is_private:
            return 'private'
        if obj.is_loopback:
            return 'loopback'
        if obj.is_link_local:
            return 'link-local'
        if obj.is_reserved:
            return 'reserved'
        return 'non-public'
    except ValueError:
        return '-'


def parse_email_datetime(value):
    if not value or value == '-':
        return None
    try:
        return parsedate_to_datetime(value)
    except Exception:
        return None


def format_utc_datetime(value):
    dt = parse_email_datetime(value)
    if not dt or not dt.tzinfo:
        return '-'
    return dt.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')


def format_timedelta(delta):
    seconds = int(delta.total_seconds())
    sign = ''
    if seconds < 0:
        sign = '-'
        seconds = abs(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days:
        parts.append(f'{days}d')
    if hours:
        parts.append(f'{hours}h')
    if minutes:
        parts.append(f'{minutes}m')
    if seconds or not parts:
        parts.append(f'{seconds}s')
    return sign + ' '.join(parts)


def fmt_list(values):
    return ', '.join(values) if values else '-'
