import re
from .utils import clean_header


def extract_auth_value(text, key):
    m = re.search(rf'\b{re.escape(key)}\s*=\s*([a-zA-Z0-9_-]+)', text, re.I)
    return m.group(1).lower() if m else '-'


def extract_dmarc_policy(text):
    for pattern in (r'\bp=([a-zA-Z0-9_-]+)', r'\bpolicy=([a-zA-Z0-9_-]+)', r'\bdmarc[^;]*\bpolicy\.evaluated\s*=\s*([a-zA-Z0-9_-]+)'):
        m = re.search(pattern, text, re.I)
        if m:
            return m.group(1).lower()
    return '-'


def extract_authentication_results(msg):
    results = []
    for header in ('Authentication-Results', 'ARC-Authentication-Results'):
        for value in msg.get_all(header, []):
            clean = clean_header(value)
            results.append({
                'header': header,
                'spf': extract_auth_value(clean, 'spf'),
                'dkim': extract_auth_value(clean, 'dkim'),
                'dmarc': extract_auth_value(clean, 'dmarc'),
                'dmarc_policy': extract_dmarc_policy(clean),
                'raw': clean,
            })
    return results


def extract_received_spf(msg):
    results = []
    for value in msg.get_all('Received-SPF', []):
        clean = clean_header(value)
        verdict = '-'
        m = re.match(r'^\s*(pass|fail|softfail|neutral|none|permerror|temperror)\b', clean, re.I)
        if m:
            verdict = m.group(1).lower()
        results.append({'verdict': verdict, 'raw': clean})
    return results


def extract_dkim_tag(text, tag):
    m = re.search(rf'(?:^|;\s*){re.escape(tag)}=([^;]+)', text, re.I)
    return m.group(1).strip() if m else '-'


def extract_dkim_signatures(msg):
    signatures = []
    for value in msg.get_all('DKIM-Signature', []):
        clean = clean_header(value)
        signatures.append({
            'domain': extract_dkim_tag(clean, 'd'),
            'selector': extract_dkim_tag(clean, 's'),
            'algorithm': extract_dkim_tag(clean, 'a'),
            'raw': clean,
        })
    return signatures


def summarize_auth(data):
    summary = {'spf': '-', 'dkim': '-', 'dmarc': '-', 'dmarc_policy': '-'}
    for item in data.get('auth_results', []):
        for key in ('spf', 'dkim', 'dmarc'):
            if item.get(key) and item[key] != '-':
                summary[key] = item[key]
        if item.get('dmarc_policy') and item['dmarc_policy'] != '-':
            summary['dmarc_policy'] = item['dmarc_policy']
    if summary['spf'] == '-' and data.get('received_spf'):
        summary['spf'] = data['received_spf'][0]['verdict']
    return summary
