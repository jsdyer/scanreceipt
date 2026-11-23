"""Validated append-only observations; never record upstream credentials or raw feeds."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,re,urllib.request,urllib.error,time
ROOT=Path(__file__).resolve().parents[1]
def now():return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def encode(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def digest(x):return hashlib.sha256(encode(x)).hexdigest()
def request_json(url,headers=None):
    from urllib.parse import urlsplit
    if urlsplit(url).hostname not in {'api.phishstats.info','urlhaus-api.abuse.ch','urlscan.io'}:raise ValueError('Unapproved evidence provider')
    # Never visit an indicator. Credentials stay in headers; diagnostics exclude URL/body.
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CoolCode Evidence/1.0 (+https://coolcode.ca/)',**(headers or {})}),timeout=45) as response:raw=response.read(15_000_001)
            if len(raw)>15_000_000:raise ValueError('Response exceeds 15 MB')
            return json.loads(raw)
        except urllib.error.HTTPError as exc:
            if exc.code==429:
                try:delay=int(exc.headers.get('Retry-After') or exc.headers.get('X-Rate-Limit-Reset-After') or '30')
                except ValueError:delay=30
                if attempt<2 and 0<=delay<=60:time.sleep(max(2,delay));continue
            raise RuntimeError('Provider HTTP '+str(exc.code)) from None
        except (OSError,ValueError):
            if attempt==2:raise RuntimeError('Provider unavailable or invalid JSON') from None
            time.sleep(2**attempt)
def validate(x):
    if not isinstance(x,dict) or x.get('schema')!=1 or not isinstance(x.get('records'),list) or not isinstance(x.get('sources'),list):raise ValueError('Invalid observation schema')
    if not x.get('captured_at') or not x.get('coverage'):raise ValueError('Missing capture or coverage')
    ids=[r.get('id') for r in x['records']]
    if any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids):raise ValueError('Missing or duplicate record IDs')
    if not all(str(s.get('url','')).startswith('https://') for s in x['sources']):raise ValueError('Invalid source URL')
    json.dumps(x,allow_nan=False)
    return x
def save(x,root=ROOT):
    stamp=now();x=validate({'schema':1,'captured_at':stamp,'checked_at':stamp,**x});folder=root/'data';folder.mkdir(exist_ok=True)
    old=json.loads((folder/'current.json').read_text()) if (folder/'current.json').exists() else None
    stable={k:v for k,v in x.items() if k not in ['captured_at','checked_at','digest','changes','needs_credentials']};hash_=digest(stable)
    history=json.loads((folder/'history.json').read_text()) if (folder/'history.json').exists() else []
    if old and old.get('digest')==hash_:
        old['checked_at']=stamp;old['needs_credentials']=x.get('needs_credentials',False);x=old
    else:
        x['digest']=hash_;x['changes']={'baseline':old is None,'previous_count':len(old['records']) if old else 0,'current_count':len(x['records'])}
        filename='archive/'+stamp[:7]+'/'+stamp.replace('-','').replace(':','')+'-'+hash_[:12]+'.json'
        target=root/filename;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(encode(x)+b'\n')
        history.append({'captured_at':stamp,'file':filename,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'count':len(x['records']),'baseline':old is None})
    for name,value in [('current.json',x),('history.json',history),('index.json',{'schema':1,'id':root.name,'title':json.loads((root/'tool.json').read_text())['title'],'captured_at':x['captured_at'],'checked_at':stamp,'records':len(x['records']),'snapshots':len(history),'status':x.get('status','partial'),'coverage':x['coverage'],'sources':[{'name':s['name'],'url':s['url'],'status':s.get('status')} for s in x['sources']]})]:
        p=folder/name;temp=p.with_suffix('.tmp');temp.write_bytes(encode(value)+b'\n');temp.replace(p)
    print(f'Validated {len(x["records"])} records; retained {len(history)} snapshots')
    return x
def assemble(root,stage):
    validate(json.loads((root/'data/current.json').read_text()));history=json.loads((root/'data/history.json').read_text())
    if not history:raise ValueError('Missing retained snapshot')
    for entry in history:
        file=entry['file']
        if not re.fullmatch(r'archive/\d{4}-\d{2}/[A-Za-z0-9-]+\.json',file):raise ValueError('Invalid archive path')
        if hashlib.sha256((root/file).read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Archive checksum mismatch')
        validate(json.loads((root/file).read_text()))
    shutil.copytree(root/'data',stage/'data');shutil.copytree(root/'archive',stage/'archive')
    if (root/'evidence').exists(): shutil.copytree(root/'evidence',stage/'evidence')
