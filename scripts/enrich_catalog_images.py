from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import json,re,urllib.request

ROOT=Path(__file__).resolve().parents[1];PATH=ROOT/'data'/'catalog.json';BASE='https://7dsorigin.app'
UA='SevenDeadlySinsOriginGuide/1.1 authorized-image-index'
def find(record):
    req=urllib.request.Request(record['source_url'],headers={'User-Agent':UA})
    with urllib.request.urlopen(req,timeout=25) as response:html=response.read().decode('utf-8','replace')
    category_paths={'characters':'characters','weapons':'weapons','armor':'armor','accessories':'accessories','items':'items','pets':'pets','monsters':'monsters','elite-monsters':'monsters','field-bosses':'monsters'}
    folder=category_paths.get(record['category'])
    if not folder:return record['id'],''
    matches=re.findall(rf'(/images/{folder}/[^"&< ]+\.(?:png|webp|jpg))',html,re.I)
    return record['id'],(BASE+matches[0] if matches else '')
def main():
    payload=json.loads(PATH.read_text(encoding='utf-8'));records=payload['records'];by_id={r['id']:r for r in records};fail=0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures=[pool.submit(find,r) for r in records]
        for i,f in enumerate(as_completed(futures),1):
            try:eid,url=f.result();by_id[eid]['image_url']=url
            except Exception:fail+=1
            if i%250==0:print(f'{i}/{len(records)} failures={fail}',flush=True)
    PATH.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print('images',sum(bool(r['image_url']) for r in records),'failures',fail)
if __name__=='__main__':main()

