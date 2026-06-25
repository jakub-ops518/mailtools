import socket
from .utils import is_public_ip, unique_keep_order


def dns_lookup_for_ip(ip):
    result = {'ip': ip, 'ptr': '-', 'forward_ips': [], 'forward_confirmed': False, 'error': None}
    try:
        ptr, _, _ = socket.gethostbyaddr(ip)
        result['ptr'] = ptr
        try:
            _, _, forward_ips = socket.gethostbyname_ex(ptr)
            result['forward_ips'] = forward_ips
            result['forward_confirmed'] = ip in forward_ips
        except Exception:
            pass
    except Exception as e:
        result['error'] = str(e)
    return result


def add_lookup(data):
    ips = []
    for hop in data.get('server_hops', []):
        for key in ('from_ip', 'by_ip'):
            ip = hop.get(key)
            if ip and ip != '-' and is_public_ip(ip):
                ips.append(ip)
    data['lookup'] = [dns_lookup_for_ip(ip) for ip in unique_keep_order(ips)]
