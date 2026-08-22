from difflib import SequenceMatcher
from rapidocr_onnxruntime import RapidOCR
from app.database import connect

_engine=None
def analyze_screenshot(path):
    global _engine
    if _engine is None:_engine=RapidOCR()
    result,_elapsed=_engine(path)
    lines=[item[1].strip() for item in (result or []) if len(item)>2 and item[2]>=0.35]
    text=' '.join(lines)
    compact=text.lower().replace(' ','')
    matches=[]
    with connect() as con:
        rows=con.execute('SELECT id,category,name_ko,name_en FROM catalog').fetchall()
    for row in rows:
        candidates=[row['name_ko'],row['name_en']]
        score=max((1.0 if (v and v.lower().replace(' ','') in compact) else SequenceMatcher(None,v.lower().replace(' ',''),compact).quick_ratio()) for v in candidates if v)
        if score>=0.42:matches.append({'id':row['id'],'category':row['category'],'name':row['name_ko'],'confidence':round(score,2)})
    matches.sort(key=lambda x:x['confidence'],reverse=True)
    return {'ocr_text':text,'lines':lines,'matches':matches[:20]}

