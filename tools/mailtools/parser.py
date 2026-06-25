import re
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, getaddresses
from .utils import clean_header, unique_keep_order, format_utc_datetime
from .hops import extract_server_hops, first_received_datetime
from .auth import extract_authentication_results, extract_received_spf, extract_dkim_signatures, summarize_auth
from .lookup import add_lookup
from .urls import extract_urls


def extract_basic_headers(msg):
    date = clean_header(msg.get('Date'))
    return {
        'subject': clean_header(msg.get('Subject')),
        'date': date,
        'date_utc': format_utc_datetime(date),
        'date_source': 'Date' if date != '-' else '-',
        'message_id': clean_header(msg.get('Message-ID')),
        'reply_to': clean_header(msg.get('Reply-To')),
        'return_path': clean_header(msg.get('Return-Path')),
    }


def extract_postfix_from(msg):
    for received in msg.get_all('Received', []):
        m = re.search(r'envelope-from\s*=\s*[<\"]?([^>\s\";]+)', received, re.I)
        if m:
            return m.group(1)
    for received in msg.get_all('Received', []):
        m = re.search(r'\bfrom\s+<([^>]+)>', received, re.I)
        if m:
            return m.group(1)
    return_path = msg.get('Return-Path')
    if return_path:
        _, addr = parseaddr(return_path)
        if addr:
            return addr
    return None


def extract_header_from(msg):
    value = msg.get('From')
    if not value:
        return None
    _, addr = parseaddr(value)
    return addr or value


def extract_recipients(msg):
    recipients = {}
    for header in ('To', 'Cc', 'Bcc'):
        values = msg.get_all(header, [])
        parsed = getaddresses(values)
        recipients[header.lower()] = [addr for _, addr in parsed if addr]
    return recipients


def extract_envelope_recipients(msg):
    found = []
    for header in ('Delivered-To', 'X-Original-To'):
        for value in msg.get_all(header, []):
            _, addr = parseaddr(value)
            if addr:
                found.append(addr)
    for received in msg.get_all('Received', []):
        found.extend(re.findall(r'\bfor\s+<([^>]+)>', received, re.I))
    return unique_keep_order(found)


def classify_eml(msg, data):
    content_type = msg.get_content_type().lower()
    subject = str(msg.get('Subject') or '').lower()
    from_addr = str(msg.get('From') or '').lower()
    auto_submitted = str(msg.get('Auto-Submitted') or '').lower()
    dsn_headers = (msg.get('Diagnostic-Code'), msg.get('Final-Recipient'), msg.get('Action'), msg.get('Status'), msg.get('Remote-MTA'), msg.get('Reporting-MTA'))
    defects = getattr(msg, 'defects', [])
    is_dsn = (
        content_type == 'multipart/report'
        or 'delivery status notification' in subject
        or 'undelivered mail' in subject
        or 'mail delivery failed' in subject
        or 'returned mail' in subject
        or 'mailer-daemon' in from_addr
        or any(dsn_headers)
    )
    if is_dsn:
        kind = 'delivery-status-notification'
    elif data.get('server_hops'):
        kind = 'normal-email'
    else:
        kind = 'incomplete-or-header-only'
    structure = 'usable'
    notes = []
    if not data.get('server_hops'):
        structure = 'incomplete'; notes.append('Missing Received headers')
    if not data.get('header_from'):
        structure = 'incomplete'; notes.append('Missing From header')
    if not data.get('to') and not data.get('envelope_recipients'):
        notes.append('Missing recipient information')
    if data.get('date_source') == 'Received':
        notes.append('Missing Date header, using Received timestamp')
    if data.get('message_id') == '-':
        notes.append('Missing Message-ID')
    if defects:
        structure = 'possibly-malformed'
        notes.extend([type(d).__name__ for d in defects])
    return {'kind': kind, 'structure': structure, 'notes': unique_keep_order(notes), 'auto_submitted': auto_submitted or '-'}


def parse_eml(path, include_urls=False, include_lookup=False):
    with open(path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    server_hops = extract_server_hops(msg)
    basic = extract_basic_headers(msg)
    if basic['date'] == '-':
        fallback_date = first_received_datetime(server_hops)
        basic['date'] = fallback_date
        basic['date_utc'] = format_utc_datetime(fallback_date)
        basic['date_source'] = 'Received' if fallback_date != '-' else '-'
    data = {
        'file': str(path), **basic,
        'postfix_from': extract_postfix_from(msg),
        'header_from': extract_header_from(msg),
        'envelope_recipients': extract_envelope_recipients(msg),
        'server_hops': server_hops,
        'auth_results': extract_authentication_results(msg),
        'received_spf': extract_received_spf(msg),
        'dkim_signatures': extract_dkim_signatures(msg),
        'raw_headers': {
            'received': [clean_header(x) for x in msg.get_all('Received', [])],
            'authentication_results': [clean_header(x) for x in msg.get_all('Authentication-Results', [])],
            'arc_authentication_results': [clean_header(x) for x in msg.get_all('ARC-Authentication-Results', [])],
            'received_spf': [clean_header(x) for x in msg.get_all('Received-SPF', [])],
            'dkim_signature': [clean_header(x) for x in msg.get_all('DKIM-Signature', [])],
        },
        **extract_recipients(msg),
    }
    data['auth_summary'] = summarize_auth(data)
    data['message_status'] = classify_eml(msg, data)
    if include_urls:
        data['urls'] = extract_urls(msg)
    if include_lookup:
        add_lookup(data)
    return data
