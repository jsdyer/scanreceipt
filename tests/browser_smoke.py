"""CI-only browser coverage at a project subpath. Fixture data is test-only."""
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,shutil,tempfile,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def fixture(sid,host,time):
 return {'task':{'uuid':sid,'visibility':'public','url':'https://'+host+'/?secret=discard','time':time},'page':{'url':'https://'+host+'/','domain':host,'title':'<img src=x onerror=alert(1)>','asn':'AS64500'},'data':{'requests':[{'request':{'type':'Document','request':{'url':'https://'+host+'/x?token=SECRET','method':'GET'},'redirectResponse':{'url':'http://'+host+'/','status':301}},'response':{'response':{'status':200,'mimeType':'text/html'}}}]}}
def main():
 screenshots=ROOT/'browser-checks';screenshots.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  shutil.copytree(ROOT/'dist',Path(tmp)/'example-tool');server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=tmp));threading.Thread(target=server.serve_forever,daemon=True).start()
  try:
   with sync_playwright() as p:
    browser=p.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];requests=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url));page.route('https://coolcode.ca/scanreceipt/evidence/**',lambda route:route.fulfill(path=str(ROOT/'dist/evidence'/route.request.url.rsplit('/',1)[1])));page.goto(f'http://127.0.0.1:{server.server_port}/example-tool/');page.wait_for_function("document.querySelector('#checked').textContent.includes('T')");page.screenshot(path=str(screenshots/'desktop.png'),full_page=True)
    if ROOT.name=='maplephish':
     page.locator('#signal-kind').select_option('malware');assert 'URLhaus' in page.locator('#brands').inner_text();page.locator('#signal-kind').select_option('phishing');page.locator('#brands .row-button').first.click();assert page.locator('#aggregate-detail').is_visible()
     row={'id':123,'url':'https://interac-TEST.example/path?token=SECRET','title':'<img src=x onerror=alert(1)>','asn':'AS64500','date':'2026-01-02'};page.locator('#input').fill(json.dumps([row]));page.locator('#import-button').click();assert '1 matching' in page.locator('#result-count').inner_text();page.locator('#rows .row-button').click();assert '<img' in page.locator('#evidence-detail').inner_text();assert 'SECRET' not in page.locator('#rows').inner_text();assert page.locator('img').count()==0
     with page.expect_download() as download:page.locator('#export-csv').click()
     assert download.value.suggested_filename.endswith('.csv');page.locator('#kind').select_option('malware');assert page.locator('#rows tr').count()==0;page.locator('#kind').select_option('');page.locator('#q').fill('unmatched');assert page.locator('#rows tr').count()==0;page.locator('#q').fill('');page.locator('#clear').click();assert page.locator('#rows tr').count()==0
    else:
     page.locator('#target-settings').filter(has_text='hackme.ca').wait_for(state='attached');assert 'Capture and publish' in page.locator('#manage').inner_text();page.locator('#manage summary').click();initial=page.locator('.receipt').count();assert initial>=3;page.locator('.receipt button').first.click();assert page.locator('#receipt-detail img').count()==1;page.wait_for_function("document.querySelector('#receipt-detail img').naturalWidth > 0");page.locator('#find-scans').click();assert 'HTTPS' in page.locator('#find-status').inner_text();page.locator('#site-url').fill('https://coolcode.ca/');page.locator('#find-scans').click();assert 'urlscan.io/search/' in page.locator('#find-links a').get_attribute('href');
     a='11111111-1111-4111-8111-111111111111';b='22222222-2222-4222-8222-222222222222'
     for sid,host,date in [(a,'alpha.example','2026-01-01T00:00:00Z'),(b,'beta.example','2026-01-02T00:00:00Z')]:page.locator('#input').fill(json.dumps(fixture(sid,host,date)));page.locator('#import-button').click()
     assert page.locator('.receipt').count()==initial+2;page.locator('.receipt').filter(has_text='beta.example').locator('button').click();assert page.locator('#receipt-detail').is_visible();assert page.locator('img').count()==0;assert 'SECRET' not in page.locator('#receipt-detail').inner_text();assert '<img' in page.locator('.receipt').filter(has_text='beta.example').inner_text()
     page.locator('#before').select_option(a);page.locator('#after').select_option(b);page.locator('#compare-button').click();assert 'beta[.]example' in page.locator('#comparison').inner_text();assert 'alpha[.]example' in page.locator('#comparison').inner_text()
     with page.expect_download() as download:page.locator('#export-json').click()
     assert download.value.suggested_filename.endswith('.json');page.locator('#scan-id').fill(a);page.locator('#lookup').click();assert page.locator('#lookup-links a').count()==2;assert 'api/v1/result' in page.locator('#lookup-links a').last.get_attribute('href');bad=fixture(a,'alpha.example','2026-01-01');bad['task']['visibility']='private';page.locator('#input').fill(json.dumps(bad));page.locator('#import-button').click();assert 'Only explicitly public' in page.locator('#status').inner_text();page.locator('#input').fill('');page.locator('#q').fill('no-match');assert page.locator('.receipt').count()==0;page.locator('#q').fill('')
    page.screenshot(path=str(screenshots/'evidence-desktop.png'),full_page=True);page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth');page.screenshot(path=str(screenshots/'mobile.png'),full_page=True);assert not errors,errors;assert not any('.example/' in u for u in requests),requests;browser.close()
   print('Browser checks passed: data, safe imports, filters, exports, source boundaries and mobile layout')
  finally:server.shutdown()
if __name__=='__main__':main()
