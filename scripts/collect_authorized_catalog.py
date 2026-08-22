"""Build the offline catalog from authorized public pages and sitemap.

This collector deliberately does not call /api routes. It reads the public
sitemap and ordinary localized detail pages, with bounded concurrency.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
import json, re, time, urllib.request, urllib.parse

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'catalog.json'
BASE='https://7dsorigin.app'
CATEGORIES={'characters','weapons','armor','accessories','items','pets','monsters','elite-monsters','field-bosses','effects'}
UA='SevenDeadlySinsOriginGuide/1.0 authorized-catalog-contact: GitHub choivoo'

def get(url, retries=3):
    for attempt in range(retries):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept-Language':'ko,en;q=0.8'})
            with urllib.request.urlopen(req,timeout=25) as res:return res.read().decode('utf-8','replace')
        except Exception:
            if attempt==retries-1:raise
            time.sleep(1.5*(attempt+1))

def meta(html,name=None,prop=None):
    key='name' if name else 'property'; value=name or prop
    patterns=[rf'<meta[^>]+{key}="{re.escape(value)}"[^>]+content="([^"]*)"',rf'<meta[^>]+content="([^"]*)"[^>]+{key}="{re.escape(value)}"']
    for p in patterns:
        m=re.search(p,html,re.I)
        if m:return unescape(m.group(1)).strip()
    return ''

def title(html):
    m=re.search(r'<title>(.*?)</title>',html,re.I|re.S)
    return unescape(m.group(1)).split(' — ')[0].strip() if m else ''

def collect_one(url):
    route=url.split('/en/',1)[1]; category,slug=route.split('/',1)
    en=get(url); ko_url=url.replace('/en/','/ko/',1); ko=get(ko_url)
    asset=re.search(r'(?:url=|src=\\?"|srcSet=\\?")((?:%2F|/|https?)[^"& ]*/images/(?:weapons|items|armor|accessories|characters|pets|monsters)/[^"& ]+\.(?:png|webp|jpg))',en,re.I)
    asset_url=unescape(urllib.parse.unquote(asset.group(1))) if asset else ''
    if asset_url.startswith('/'):asset_url=BASE+asset_url
    return {'id':f'{category}:{slug}','category':category,'slug':slug,'name_ko':title(ko) or title(en),'name_en':title(en),'description_ko':meta(ko,name='description'),'description_en':meta(en,name='description'),'source_url':url,'image_url':asset_url,'confidence':'authorized_public_page'}

def main():
    sitemap=get(BASE+'/sitemap.xml')
    urls=sorted(set(unescape(m.group(1)) for m in re.finditer(r'href="(https://7dsorigin\.app/en/[^" ]+)"',sitemap)))
    urls=[u for u in urls if u.split('/en/',1)[1].split('/',1)[0] in CATEGORIES and '/' in u.split('/en/',1)[1]]
    records=[];failed=[]
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures={pool.submit(collect_one,u):u for u in urls}
        for i,f in enumerate(as_completed(futures),1):
            try:records.append(f.result())
            except Exception as exc:failed.append({'url':futures[f],'error':str(exc)})
            if i%100==0:print(f'{i}/{len(urls)} records={len(records)} failed={len(failed)}',flush=True)
    records.sort(key=lambda x:(x['category'],x['name_ko']))
    payload={'generated_at':datetime.now(timezone.utc).isoformat(),'source':BASE,'authorized':True,'records':records,'failed':failed}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'WROTE {OUT} records={len(records)} failed={len(failed)}')

if __name__=='__main__':main()

