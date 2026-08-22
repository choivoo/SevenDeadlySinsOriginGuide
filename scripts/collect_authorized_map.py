"""Download the authorized Britannia marker dataset using a short-lived session."""
from datetime import datetime,timezone
from pathlib import Path
import json,urllib.parse,urllib.request

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'data'/'map_markers.json';BASE='https://7dsorigin.app'
HEADERS={'User-Agent':'SevenDeadlySinsOriginGuide/1.1 authorized-data-client'}
def request(url,method='GET'):
    req=urllib.request.Request(url,headers=HEADERS,method=method)
    with urllib.request.urlopen(req,timeout=60) as response:return json.loads(response.read())
def main():
    token=request(BASE+'/api/map/session','POST')['token']
    query=urllib.parse.urlencode({'t':token,'lang':'ko','map':'britannia'})
    markers=request(BASE+'/api/map/markers?'+query)['markers']
    payload={'generated_at':datetime.now(timezone.utc).isoformat(),'map':'britannia','authorized':True,'markers':markers}
    OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'WROTE {OUT} markers={len(markers)}')
if __name__=='__main__':main()

