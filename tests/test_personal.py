import unittest,sys,json,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import urlscan_check
from collect import target_url
class PersonalTests(unittest.TestCase):
 def test_owned_target_validation(self):
  self.assertEqual(target_url('https://coolcode.ca/rackexpiry/'),'https://coolcode.ca/rackexpiry/')
  for value in ['http://coolcode.ca/','https://evil.example/','https://coolcode.ca/?token=x','https://user:pass@coolcode.ca/','https://coolcode.ca:444/']:
   with self.assertRaises(ValueError):target_url(value)
  with self.assertRaises(ValueError):urlscan_check.allowed_target('https://coolcode.ca/secret',{'urlscan_targets':['https://coolcode.ca/']})
 def test_one_submission_and_provider_links_without_saved_report(self):
  sid='12345678-1234-4234-8234-123456789abc'
  with tempfile.TemporaryDirectory() as d:
   summary=Path(d)/'summary.md'
   with patch.dict('os.environ',{'URLSCAN_API_KEY':'test-secret','GITHUB_STEP_SUMMARY':str(summary)}),patch.object(urlscan_check,'call',side_effect=[{'uuid':sid},{'sensitive':'NOT_IN_SUMMARY'}]) as request,patch.object(urlscan_check.time,'sleep'):
    urlscan_check.run('https://coolcode.ca/')
   self.assertEqual(request.call_count,2)
   self.assertEqual(request.call_args_list[0].args[2],{'url':'https://coolcode.ca/','visibility':'public'})
   text=summary.read_text();self.assertIn('/result/'+sid,text);self.assertNotIn('NOT_IN_SUMMARY',text);self.assertNotIn('test-secret',text)
