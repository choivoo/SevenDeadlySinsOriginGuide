from hashlib import sha256
from pathlib import Path
import urllib.request
from app.config import USER_DIR

CACHE=USER_DIR/'image_cache';CACHE.mkdir(exist_ok=True)
def cached_image(url):
    if not url:return None
    suffix=Path(url.split('?',1)[0]).suffix or '.img';target=CACHE/(sha256(url.encode()).hexdigest()+suffix)
    if target.exists() and target.stat().st_size>100:return target
    request=urllib.request.Request(url,headers={'User-Agent':'SevenDeadlySinsOriginGuide/1.1'})
    with urllib.request.urlopen(request,timeout=20) as response:data=response.read()
    if len(data)<100:raise ValueError('이미지 응답이 비어 있습니다.')
    temp=target.with_suffix(target.suffix+'.new');temp.write_bytes(data);temp.replace(target);return target

