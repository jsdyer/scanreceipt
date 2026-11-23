"""Read existing public scans only. This module has no scan-submission API."""
from archive import ROOT,save,request_json
from urllib.parse import urlencode,urlsplit
from collections import Counter
import os,re,json
UUID=re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
def safe_url(value):
    try:
        x=urlsplit(value)
        if x.scheme not in ['http','https'] or not x.hostname:return 'Unavailable'
        return x.scheme+'://'+x.hostname+((':'+str(x.port)) if x.port else '')+(x.path or '/')+('?[values removed]' if x.query else '')
    except (ValueError,TypeError):return 'Unavailable'
def normalize(x,allowed=None):
    task=x.get('task') or {};page=x.get('page') or {};sid=task.get('uuid','');url=task.get('url','');host=urlsplit(url).hostname
    if not UUID.fullmatch(sid):raise ValueError('Invalid public scan ID')
    if task.get('visibility')!='public':raise ValueError('Only explicitly public scans may be retained')
    if allowed is not None and host not in allowed:raise ValueError('Scan URL outside owned-domain allowlist')
    requests=[];redirects=[]
    raw=(x.get('data') or {}).get('requests')
    if not isinstance(raw,list):raise ValueError('Invalid requests array')
    for item in raw[:2000]:
        wrapper=item.get('request') or {};req=wrapper.get('request') or {};response=(item.get('response') or {}).get('response') or {};u=req.get('url') or response.get('url') or ''
        status=response.get('status');record={'url':safe_url(u),'domain':urlsplit(u).hostname or 'Unknown','method':req.get('method','GET'),'type':wrapper.get('type') or item.get('type') or 'Unknown','status':status if isinstance(status,(int,float)) else None,'mime':response.get('mimeType',''),'ip':response.get('remoteIPAddress','')}
        requests.append(record)
        redirect=wrapper.get('redirectResponse') or item.get('redirectResponse')
        if isinstance(redirect,dict):redirects.append({'from':safe_url(redirect.get('url','')),'to':safe_url(u),'status':redirect.get('status')})
    return {'id':sid,'domain':page.get('domain') or host,'submitted_url':safe_url(url),'final_url':safe_url(page.get('url','')),'scanned_at':task.get('time',''),'visibility':'public','source':'urlscan.io','source_url':'https://urlscan.io/result/'+sid+'/','screenshot_url':'https://urlscan.io/screenshots/'+sid+'.png','title':str(page.get('title') or '')[:500],'country':page.get('country') or 'Not reported','asn':page.get('asn') or 'Not reported','asn_name':page.get('asnname') or 'Not reported','requests':requests,'request_count':len(raw),'requests_truncated':len(raw)>2000,'redirects':redirects,'domains':sorted(set(r['domain'] for r in requests)),'privacy':'Query values, fragments, credentials, headers, cookies and request bodies excluded.'}