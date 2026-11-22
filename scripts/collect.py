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
def run():
    config=json.loads((ROOT/'config.json').read_text());allowed=config['owned_domains']
    if not allowed or len(allowed)>5 or any(not re.fullmatch(r'[a-z0-9.-]+',d) for d in allowed):raise ValueError('Invalid owned-domain allowlist')
    headers={'API-Key':os.environ['URLSCAN_API_KEY']} if os.getenv('URLSCAN_API_KEY') else {}
    checks=[];candidates={};receipts=[]
    for domain in allowed:
        q='domain:'+domain+' AND task.visibility:public AND date:>now-'+str(min(30,int(config.get('search_days',30))))+'d'
        data=request_json('https://urlscan.io/api/v1/search/?'+urlencode({'q':q,'size':min(5,int(config.get('maximum_results_per_domain',5)))}),headers)
        if not isinstance(data.get('results'),list):raise ValueError('Invalid search response')
        checks.append({'domain':domain,'matching_results':data.get('total'),'returned_results':len(data['results']),'history_limit_days':data.get('search_date_limit_days'),'window_days':min(30,int(config.get('search_days',30)))})
        for r in data['results']:
            sid=r.get('_id') or (r.get('task') or {}).get('uuid','')
            if UUID.fullmatch(sid):candidates[sid]=True
    if config.get('publish_receipts'):
        if not config.get('permission_note','').strip():raise ValueError('Document public-republication permission')
        for sid in config.get('existing_public_scan_ids',[]):
            if not UUID.fullmatch(sid):raise ValueError('Invalid manual scan ID')
            candidates[sid]=True
        for sid in list(candidates)[:12]:receipts.append(normalize(request_json('https://urlscan.io/api/v1/result/'+sid+'/',headers),allowed))
    warnings=['No new scan is submitted. Existing public results only. Search history depends on the account tier.']
    if not config.get('publish_receipts'):warnings.append('Public receipt republication is disabled pending provider permission. Import an existing result JSON locally to inspect and save a sanitized receipt.')
    if not any(c['returned_results'] for c in checks):warnings.append('No existing public scans were returned for the selected owned domains and search window. This does not mean the sites have never been scanned.')
    return save({'needs_credentials':not bool(os.getenv('URLSCAN_API_KEY')),'records':receipts,'search_checks':checks,'sources':[{'name':'urlscan.io','url':'https://docs.urlscan.io/','status':'search checked','policy':'https://urlscan.io/terms/','detail':'Existing public search only; no submission endpoint.'}],'status':'ready' if receipts else 'import ready','coverage':'Owned domains: '+', '.join(allowed)+'. Last 30 days; at most 5 results per domain. Public receipts require documented provider permission.','warnings':warnings,'policy_checked':'2026-11-22','publication_enabled':bool(config.get('publish_receipts'))})
if __name__=='__main__':
    try:run()
    except Exception as e:raise SystemExit('Collection stopped; previous data retained. '+str(e)) from None
