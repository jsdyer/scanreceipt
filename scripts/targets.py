"""Explicit owner scope shared by browser captures and the urlscan client."""
import json,re
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[1]

def settings(root=ROOT):
    config=json.loads((root/'config.json').read_text())
    hosts=config.get('owned_hosts',[])
    if not 1<=len(hosts)<=30 or len(set(hosts))!=len(hosts) or any(not re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*\.[a-z]{2,}',h) for h in hosts):
        raise ValueError('Configure one to thirty distinct public owned hostnames')
    for key in ('capture_urls','urlscan_targets'):
        values=config.get(key,[])
        if not 1<=len(values)<=30 or len(set(values))!=len(values):raise ValueError('Configure distinct public URLs')
        for value in values:target_url(value,config)
    return config

def host_allowed(host,config):
    return host in config['owned_hosts'] or (bool(host) and host.startswith('www.') and host[4:] in config['owned_hosts'])

def target_url(value,config=None):
    if config is None:config=json.loads((ROOT/'config.json').read_text())
    u=urlsplit(value)
    if (u.scheme!='https' or not host_allowed(u.hostname,config) or u.port not in (None,443)
            or u.username or u.password or u.query or u.fragment or any(ord(c)<33 for c in value)):
        raise ValueError('Use a configured owned HTTPS page without credentials, query strings or fragments')
    return value
