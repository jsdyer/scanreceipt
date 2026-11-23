"""Capture our public pages ourselves; no provider database is copied."""
import json
import uuid
from urllib.parse import urlsplit
from archive import ROOT, now, save
from urlscan_import import normalize, safe_url

OWNED = {'coolcode.ca', 'jsdyer.github.io'}

def target_url(value):
    u = urlsplit(value)
    if (u.scheme != 'https' or u.hostname not in OWNED or u.port not in (None,443)
            or u.username or u.password or u.query or u.fragment):
        raise ValueError('Use an allowlisted public HTTPS page without credentials or query strings')
    return value

def run(root=ROOT):
    from playwright.sync_api import sync_playwright
    config = json.loads((root/'config.json').read_text())
    urls = config['capture_urls']
    if not 1 <= len(urls) <= 5 or len(set(urls)) != len(urls):
        raise ValueError('Select one to five distinct owned pages')
    for u in urls: target_url(u)
    records = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for url in urls:
            stamp, sid = now(), str(uuid.uuid4())
            context = browser.new_context(viewport={'width':1280,'height':900}, locale='en-CA', timezone_id='UTC', service_workers='block')
            page = context.new_page()
            def route(r):
                q=r.request; u=urlsplit(q.url)
                if q.method not in ('GET','HEAD') or u.scheme not in ('http','https') or u.path.endswith('/tool-metrics.js'):
                    r.abort(); return
                if q.is_navigation_request() and q.frame == page.main_frame and u.hostname not in OWNED:
                    r.abort(); return
                r.continue_()
            page.route('**/*', route)
            requests, redirects = [], []
            def response(r):
                q=r.request
                if len(requests) >= 2000: return
                requests.append({'url':safe_url(q.url),'domain':urlsplit(q.url).hostname or 'Unknown',
                    'method':q.method,'type':q.resource_type,'status':r.status,'mime':r.headers.get('content-type',''),'ip':''})
                prior=q.redirected_from
                if prior:
                    previous=prior.response()
                    redirects.append({'from':safe_url(prior.url),'to':safe_url(q.url),'status':previous.status if previous else None})
            page.on('response', response)
            result = page.goto(url, wait_until='networkidle', timeout=60000)
            if result is None or result.status >= 400: raise ValueError('Owned page could not be captured')
            page.wait_for_timeout(2000)
            target_url(page.url)
            height=page.evaluate('document.documentElement.scrollHeight')
            clipped=height>20000
            dest=root/'evidence'/f'{sid}.jpg';dest.parent.mkdir(exist_ok=True)
            if clipped: page.screenshot(path=str(dest),type='jpeg',quality=65,clip={'x':0,'y':0,'width':1280,'height':20000})
            else: page.screenshot(path=str(dest),type='jpeg',quality=65,full_page=True)
            records.append({'id':sid,'domain':urlsplit(page.url).hostname,'submitted_url':url,'final_url':safe_url(page.url),
                'scanned_at':stamp,'visibility':'public','source':'CoolCode Chromium','source_url':url,
                'screenshot_url':f'https://coolcode.ca/scanreceipt/evidence/{sid}.jpg','title':page.title(),
                'country':'Runner location not inferred','asn':'Not measured','asn_name':'Not measured',
                'requests':requests,'request_count':len(requests),'requests_truncated':len(requests)>=2000,
                'redirects':redirects,'domains':sorted({r['domain'] for r in requests}),
                'viewport':{'width':1280,'height':900},'screenshot_clipped':clipped,'browser_version':browser.version,
                'privacy':'Fresh unsigned-in browser; POST requests and metrics blocked; no headers, cookies or bodies retained.'})
            context.close()
        browser.close()
    old=json.loads((root/'data/current.json').read_text()) if (root/'data/current.json').exists() else {}
    recent=[r for r in old.get('records',[]) if r.get('source')=='CoolCode Chromium']
    records=(records+recent)[:30]
    return save({'collector':'owned-chromium-v1','needs_credentials':False,'records':records,'status':'ready',
        'coverage':'Daily browser captures of '+', '.join(urls)+'. Fresh desktop Chromium; no sign-in or consent interaction.',
        'capture_urls':urls,'sources':[{'name':'CoolCode browser capture','url':'https://github.com/jsdyer/scanreceipt',
            'status':'captured directly','detail':'Our own Chromium screenshots and network observations; independent of urlscan.'}],
        'warnings':[]},root)

if __name__=='__main__':
    try: run()
    except Exception as e: raise SystemExit('Capture failed; previous deployment retained. '+str(e)) from None
