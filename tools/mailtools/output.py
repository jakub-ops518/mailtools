from urllib.parse import urlparse
from datetime import timezone
from .utils import LINE, fmt_list, unique_keep_order, parse_email_datetime, format_timedelta
from .hops import build_mail_path_nodes


def section(title):
    print(); print(title); print(LINE)


def human_message_kind(value):
    return {'normal-email':'Normal email','delivery-status-notification':'Delivery failure / bounce','incomplete-or-header-only':'Incomplete or header-only message'}.get(value, value or '-')


def human_structure(value):
    return {'usable':'Usable','incomplete':'Incomplete','possibly-malformed':'Possibly malformed'}.get(value, value or '-')


def fmt_node(node):
    host = node.get('host') or '-'; ip = node.get('ip') or '-'; kind = node.get('ip_type') or '-'
    if ip != '-' and host in (ip, f'[{ip}]'):
        return f'{ip} ({kind})'
    if ip != '-':
        return f'{ip} ({kind})\n{host}'
    return host


def fmt_endpoint(host, ip):
    if ip and ip != '-' and host and host != '-' and host not in (ip, f'[{ip}]'):
        return f'{host} [{ip}]'
    if ip and ip != '-':
        return ip
    return host or '-'


def print_message_status(data):
    s = data.get('message_status', {})
    section('MESSAGE STATUS')
    print(f"Kind:             {human_message_kind(s.get('kind'))}")
    print(f"Structure:        {human_structure(s.get('structure'))}")
    print(f"Notes:            {fmt_list(s.get('notes'))}")


def print_default(data):
    print('FILE'); print(LINE); print(f"File:             {data['file']}")
    section('MESSAGE')
    print(f"Subject:          {data.get('subject') or '-'}")
    print(f"Date:             {data.get('date') or '-'}")
    print(f"Date UTC:         {data.get('date_utc') or '-'}")
    print(f"Date Source:      {data.get('date_source') or '-'}")
    print(f"Message-ID:       {data.get('message_id') or '-'}")
    print_message_status(data)
    section('ADDRESSES')
    print(f"Envelope From:    {data.get('postfix_from') or '-'}")
    print(f"Header From:      {data.get('header_from') or '-'}")
    print(f"Return-Path:      {data.get('return_path') or '-'}")
    print(f"Reply-To:         {data.get('reply_to') or '-'}")
    print(f"Envelope Rcpt:    {fmt_list(data.get('envelope_recipients'))}")
    print(f"To:               {fmt_list(data.get('to'))}")
    print(f"Cc:               {fmt_list(data.get('cc'))}")
    print(f"Bcc:              {fmt_list(data.get('bcc'))}")
    auth = data['auth_summary']
    section('AUTHENTICATION')
    print(f"SPF:              {auth['spf'].upper()}")
    print(f"DKIM:             {auth['dkim'].upper()}")
    print(f"DMARC:            {auth['dmarc'].upper()}")
    print(f"DMARC Policy:     {auth['dmarc_policy'].upper()}")
    section('MAIL PATH')
    nodes = build_mail_path_nodes(data.get('server_hops', []))
    if not nodes:
        print('-'); return
    for i, node in enumerate(nodes, 1):
        for line in fmt_node(node).splitlines(): print(line)
        if i != len(nodes): print('        |'); print('        v')


def print_brief(data):
    auth = data['auth_summary']; s = data.get('message_status', {})
    print(f"Subject       : {data.get('subject') or '-'}")
    print(f"Date UTC      : {data.get('date_utc') or '-'}")
    print(f"Kind          : {human_message_kind(s.get('kind'))}")
    print(f"Structure     : {human_structure(s.get('structure'))}")
    print(f"Envelope From : {data.get('postfix_from') or '-'}")
    print(f"Header From   : {data.get('header_from') or '-'}")
    print(f"Recipient     : {fmt_list(data.get('envelope_recipients') or data.get('to'))}")
    print(f"SPF           : {auth['spf'].upper()}")
    print(f"DKIM          : {auth['dkim'].upper()}")
    print(f"DMARC         : {auth['dmarc'].upper()}")
    print(f"DMARC Policy  : {auth['dmarc_policy'].upper()}")


def print_verbose(data):
    print_default(data); section('HOP DETAILS')
    hops = data.get('server_hops', [])
    if not hops: print('-'); return
    for i, hop in enumerate(hops, 1):
        print(f"Hop #{i}")
        print(f"  From Host : {hop['from_host']}")
        print(f"  From IP   : {hop['from_ip']} ({hop['from_ip_type']})")
        print(f"  By Host   : {hop['by_host']}")
        print(f"  By IP     : {hop['by_ip']} ({hop['by_ip_type']})")
        print(f"  Protocol  : {hop['protocol']}")
        print(f"  Queue ID  : {hop['queue_id']}")
        print()


def print_timeline(data):
    section('TIMELINE')
    hops = data.get('server_hops', [])
    if not hops: print('-'); return
    previous_dt = None
    for i, hop in enumerate(hops, 1):
        dt = parse_email_datetime(hop.get('date')); delay = '-'
        if previous_dt and dt and previous_dt.tzinfo and dt.tzinfo:
            delay = '+' + format_timedelta(dt.astimezone(timezone.utc) - previous_dt.astimezone(timezone.utc))
        print(f"Hop #{i}")
        print(f"  Time     : {hop.get('date') or '-'}")
        print(f"  Time UTC : {hop.get('date_utc') or '-'}")
        print(f"  From     : {fmt_endpoint(hop['from_host'], hop['from_ip'])}")
        print(f"  By       : {fmt_endpoint(hop['by_host'], hop['by_ip'])}")
        print(f"  Delay    : {delay}")
        print()
        if dt: previous_dt = dt


def print_lookup(data):
    section('DNS LOOKUP')
    if not data.get('lookup'):
        print('No public IP addresses found in mail path.'); return
    for item in data['lookup']:
        print(f"IP:                 {item['ip']}")
        print(f"PTR:                {item['ptr']}")
        print(f"Forward IPs:        {fmt_list(item['forward_ips'])}")
        print(f"Forward Confirmed:  {'YES' if item['forward_confirmed'] else 'NO'}")
        if item.get('error'): print(f"Error:              {item['error']}")
        print()


def print_urls(data):
    section('URLS')
    urls = data.get('urls', [])
    if not urls: print('-'); return
    domains = []
    for url in urls:
        print(url); host = urlparse(url).netloc.lower()
        if host: domains.append(host)
    section('URL DOMAINS')
    for domain in unique_keep_order(domains): print(domain)


def print_raw(data):
    section('RAW RECEIVED HEADERS')
    for i, value in enumerate(data['raw_headers'].get('received', []), 1):
        print(f'Received #{i}:'); print(value); print()
    section('RAW AUTHENTICATION HEADERS')
    any_auth = False
    for key in ('authentication_results','arc_authentication_results','received_spf','dkim_signature'):
        values = data['raw_headers'].get(key, [])
        if not values: continue
        any_auth = True; print(key + ':')
        for i, value in enumerate(values, 1): print(f'{i}. {value}')
        print()
    if not any_auth: print('-')
