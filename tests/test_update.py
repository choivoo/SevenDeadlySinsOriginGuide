import json
from app import update_service as us

def test_rejects_small_remote_catalog(monkeypatch,tmp_path):
    class Response:
        def __enter__(self):return self
        def __exit__(self,*_):pass
        def read(self):return json.dumps({'records':[{'id':'x'}]}).encode()
    monkeypatch.setattr(us.urllib.request,'urlopen',lambda *a,**k:Response())
    monkeypatch.setattr(us,'LOCAL_CATALOG',tmp_path/'catalog.json')
    try:us.update_catalog();assert False
    except ValueError:pass

