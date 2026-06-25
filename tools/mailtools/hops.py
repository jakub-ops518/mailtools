import re
from .utils import clean_header, clean_host, format_utc_datetime, ip_type, unique_keep_order


def extract_server_hops(msg):
    hops = []
    for received in reversed(msg.get_all('Received', [])):
        from_host = from_ip = by_host = by_ip = protocol = queue_id = date = '-'
        m = re.search(r'\bfrom\s+([^\s(;]+)', received, re.I)
        if m:
            from_host = clean_host(m.group(1))
        m = re.search(r'\bfrom\b.*?\[([0-9a-fA-F:.]+)\]', received, re.I | re.S)
        if m:
            from_ip = m.group(1)
        m = re.search(r'\bby\s+([^\s(;]+)', received, re.I)
        if m:
            by_host = clean_host(m.group(1))
        m = re.search(r'\bby\b.*?\[([0-9a-fA-F:.]+)\]', received, re.I | re.S)
        if m:
            by_ip = m.group(1)
        m = re.search(r'\bwith\s+([A-Z0-9]+)', received, re.I)
        if m:
            protocol = m.group(1)
        m = re.search(r'\bid\s+([^\s;]+)', received, re.I)
        if m:
            queue_id = m.group(1)
        if ';' in received:
            date = received.split(';')[-1].strip()
        hops.append({
            'from_host': from_host, 'from_ip': from_ip, 'from_ip_type': ip_type(from_ip),
            'by_host': by_host, 'by_ip': by_ip, 'by_ip_type': ip_type(by_ip),
            'protocol': protocol, 'queue_id': queue_id, 'date': date,
            'date_utc': format_utc_datetime(date), 'raw': clean_header(received),
        })
    return hops


def first_received_datetime(hops):
    for hop in reversed(hops):
        if hop.get('date') and hop['date'] != '-':
            return hop['date']
    return '-'


def build_mail_path_nodes(hops):
    nodes = []
    for hop in hops:
        nodes.append({'host': hop['from_host'], 'ip': hop['from_ip'], 'ip_type': hop['from_ip_type']})
    if hops:
        nodes.append({'host': hops[-1]['by_host'], 'ip': hops[-1]['by_ip'], 'ip_type': hops[-1]['by_ip_type']})
    result = []
    seen = set()
    for node in nodes:
        host = node.get('host') or '-'
        ip = node.get('ip') or '-'
        if host == '-' and ip == '-':
            continue
        key = ip.lower() if host in (ip, f'[{ip}]') else f'{host}|{ip}'.lower()
        if key not in seen:
            seen.add(key)
            result.append(node)
    return result
