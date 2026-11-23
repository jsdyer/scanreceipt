"""Owner-run API client: submit one allowlisted URL and return provider links only."""
import argparse,json,os,re,time,urllib.request,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
UUID=re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$',re.I)

def allowed_target(value,config):
    if value not in config['urlscan_targets']: raise ValueError('Target is not an owner-authorized public homepage')
    return value

def call(path,key,payload=None):
    body=json.dumps(payload).encode() if payload is not None else None
    req=urllib.request.Request('https://urlscan.io'+path,data=body,headers={
        'API-Key':key,'Content-Type':'application/json','User-Agent':'CoolCode Personal Scan Receipt/2.0 (+https://coolcode.ca/scanreceipt/)'})
    try:
        with urllib.request.urlopen(req,timeout=45) as response: return json.loads(response.read(10_000_000))
    except urllib.error.HTTPError as e:
        if payload is None and e.code==404: return None
        raise RuntimeError('urlscan returned HTTP '+str(e.code)+'. Submission is not automatically retried.') from None
    except (OSError,ValueError): raise RuntimeError('Provider response unavailable. Check your urlscan account before submitting again.') from None

def run(target):
    target=allowed_target(target,json.loads((ROOT/'config.json').read_text()))
    key=os.environ.get('URLSCAN_API_KEY','').strip()
    if not key: raise ValueError('Set the URLSCAN_API_KEY environment variable / repository secret')
    print('Submitting one public scan of the owner-authorized homepage. URL and results will be public on urlscan.io.')
    response=call('/api/v1/scan/',key,{'url':target,'visibility':'public'})
    sid=response.get('uuid','')
    if not UUID.fullmatch(sid): raise ValueError('Provider did not return a valid scan ID')
    sid=sid.lower(); report='https://urlscan.io/result/'+sid+'/'
    lines=['# Your urlscan report','',f'[Open the report]({report})',
        f'[Open Result API JSON](https://urlscan.io/api/v1/result/{sid}/)',
        f'[Open screenshot](https://urlscan.io/screenshots/{sid}.png)','',
        'Copy the full public Result API JSON into [Scan Receipt](https://coolcode.ca/scanreceipt/#import) to inspect, save and compare it locally.','',
        'This workflow retains links only. No provider result database, screenshot or response body is published in this repository.']
    text='\n'.join(lines)+'\n';print(text)
    if os.getenv('GITHUB_STEP_SUMMARY'): Path(os.environ['GITHUB_STEP_SUMMARY']).write_text(text)
    deadline=time.monotonic()+240
    time.sleep(30)
    while time.monotonic()<deadline:
        data=call('/api/v1/result/'+sid+'/',key)
        if data is not None:
            print('Public report is ready.');return
        time.sleep(15)
    print('Scan accepted; still processing. Open the report link later. No duplicate was submitted.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--target',default='https://coolcode.ca/');args=parser.parse_args()
    try:run(args.target)
    except Exception as e:raise SystemExit(str(e)) from None
