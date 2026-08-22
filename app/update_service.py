import json, os, urllib.request
from pathlib import Path
from app.config import USER_DIR

REMOTE_CATALOG='https://raw.githubusercontent.com/choivoo/SevenDeadlySinsOriginGuide/main/data/catalog.json'
LOCAL_CATALOG=USER_DIR/'catalog.json'

def update_catalog():
    request=urllib.request.Request(REMOTE_CATALOG,headers={'User-Agent':'SevenDeadlySinsOriginGuide/1.1'})
    with urllib.request.urlopen(request,timeout=30) as response:data=response.read()
    payload=json.loads(data.decode('utf-8'))
    records=payload.get('records',[])
    if len(records)<1000:raise ValueError('원격 카탈로그 레코드가 비정상적으로 적어 업데이트를 중단했습니다.')
    ids=[r.get('id') for r in records]
    if len(ids)!=len(set(ids)) or any(not x for x in ids):raise ValueError('원격 카탈로그 ID 검증에 실패했습니다.')
    temp=LOCAL_CATALOG.with_suffix('.json.new');temp.write_bytes(data);os.replace(temp,LOCAL_CATALOG)
    return len(records)

