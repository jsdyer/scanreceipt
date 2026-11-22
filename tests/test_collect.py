import unittest,sys,json,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from collect import normalize,safe_url
from archive import save,assemble
class CollectTests(unittest.TestCase):
 def fixture(self):return {'task':{'uuid':'11111111-1111-4111-8111-111111111111','visibility':'public','url':'https://coolcode.ca/?token=secret','time':'2026-01-01'},'page':{'url':'https://coolcode.ca/'},'data':{'requests':[{'request':{'request':{'url':'https://user:pass@coolcode.ca/a?private=secret','method':'GET'},'redirectResponse':{'url':'http://coolcode.ca','status':301}},'response':{'response':{'status':200}}}]}}
 def test_receipt_redacts_and_preserves_date_status_redirect(self):
  r=normalize(self.fixture(),['coolcode.ca']);self.assertEqual(r['scanned_at'],'2026-01-01');self.assertEqual(r['redirects'][0]['status'],301);self.assertEqual(r['requests'][0]['status'],200);self.assertNotIn('secret',json.dumps(r));self.assertNotIn('user:pass',json.dumps(r));self.assertEqual(safe_url('javascript:alert(1)'),'Unavailable')
 def test_public_allowlist_enforced(self):
  with self.assertRaisesRegex(ValueError,'allowlist'):normalize(self.fixture(),['elsewhere.example'])
  raw=self.fixture();raw['task']['visibility']='unlisted'
  with self.assertRaisesRegex(ValueError,'public'):normalize(raw,['coolcode.ca'])
 def test_archive_is_immutable_and_validated(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'tool.json').write_text('{"title":"test"}');payload={'records':[],'sources':[{'name':'source','url':'https://example.org'}],'coverage':'Known empty response'}
   save(payload,root);files=list(root.glob('archive/*/*'));original=files[0].read_bytes();save(payload,root);self.assertEqual(len(list(root.glob('archive/*/*'))),1);self.assertEqual(original,files[0].read_bytes());stage=root/'stage';stage.mkdir();assemble(root,stage);files[0].write_text('{}');
   with self.assertRaisesRegex(ValueError,'checksum'):assemble(root,root/'invalid')
