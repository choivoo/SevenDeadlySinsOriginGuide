import sqlite3, json
from contextlib import contextmanager
from datetime import date
from app.config import DATABASE_PATH, DATA_VERSION, BASE_DIR, USER_DIR

CHARACTERS = [
 ("derieri","데리엘리","Derieri","SSR","어둠","공격","건틀릿","공격 / 지원", "Ver 1.8 신규 영웅. 무기별 역할을 확인해 파티에 맞춰 운용하세요."),
 ("klotho","클로토","Clotho","SSR","바람","버스터","지팡이","버스터 / 수호", "무기와 콘텐츠에 따라 공격·수호 역할을 전환합니다."),
 ("daisy","데이지","Daisy","SSR","대지","공격","한손검","공격 / 지원", "대지 공격형 빌드와 지원형 빌드를 비교하세요."),
 ("diane","다이앤","Diane","SSR","대지","수호","도끼","공격 / 버스터 / 수호", "전방 유지력과 파티 안전성을 우선하는 수호 빌드가 있습니다."),
 ("drake","드레이크","Drake","SSR","번개","공격","랜스","공격 / 지원 / 버스터", "번개 파티의 공격 또는 지원 축으로 편성할 수 있습니다."),
 ("elaine","엘레인","Elaine","SSR","바람","공격","완드","공격 / 버스터 / 수호", "바람 무기 조합과 콘텐츠별 역할을 점검하세요."),
 ("elizabeth","엘리자베스","Elizabeth","SSR","성","수호","마도서","수호 / 지원 / 버스터", "생존이 필요한 계정에는 수호형 세팅의 가치가 높습니다."),
 ("escanor","에스카노르","Escanor","SSR","불","공격","양손검","공격 / 수호", "주력 피해 투자 후보입니다."),
 ("gowther","고서","Gowther","SSR","번개","버스터","마도서","버스터 / 지원", "파티 보조와 폭발 구간을 동시에 설계할 수 있습니다."),
 ("guila","길라","Guila","SSR","불","공격","완드","공격 / 수호 / 버스터", "불 속성 파티의 보조 공격 축입니다."),
 ("jericho","제리코","Jericho","SSR","얼음","버스터","레이피어","버스터 / 수호 / 공격", "얼음 조합의 폭발 구간에 적합합니다."),
 ("king","킹","King","SSR","성","공격","창","공격 / 수호 / 지원", "상황에 따라 공격과 지원을 전환합니다."),
 ("mannie","매니","Mannie","SSR","성","지원","스태프","지원 / 공격", "안정적인 팀 운용을 위한 지원 후보입니다."),
 ("meliodas","멜리오다스","Meliodas","SSR","어둠","공격","쌍검","공격", "주력 DPS로 육성하기 좋은 기본 공격형 영웅입니다."),
 ("merlin","멀린","Merlin","SSR","얼음","공격","스태프","공격 / 버스터", "빙결·폭발 중심 조합을 검토하세요."),
 ("bug","버그","Bug","SR","어둠","공격","단검","공격 / 지원", "초반 계정의 빈 역할을 보완하는 SR 영웅입니다."),
 ("dredrin","드레드린","Dredrin","SR","대지","수호","방패","수호 / 지원", "초반 생존 축으로 활용할 수 있습니다."),
 ("dreyfus","드레퓌스","Dreyfus","SR","물리","지원","한손검","지원 / 공격", "초반 보조 및 물리 조합 후보입니다."),
 ("gilthunder","길선더","Gilthunder","SR","번개","버스터","창","버스터 / 수호 / 공격", "번개 파티의 초기 버스터 선택지입니다."),
 ("griamore","그리어모어","Griamore","SR","물리","수호","방패","수호 / 공격 / 지원", "방어 안정성이 필요한 전투에 사용하세요."),
 ("hendrickson","헨드릭슨","Hendrickson","SR","성","수호","스태프","수호 / 공격", "지속 전투에서 수호 역할을 맡길 수 있습니다."),
 ("howzer","하우저","Howzer","SR","바람","공격","도끼","공격 / 지원 / 수호", "바람 초기 파티에 활용 가능한 다목적 영웅입니다."),
 ("slater","슬레이더","Slater","SR","불","공격","양손검","공격 / 지원 / 버스터", "불 속성 초반 딜러 후보입니다."),
 ("tioreh","티오레","Tioreh","SR","불","지원","완드","지원 / 수호", "초반 지원 자원이 부족할 때 고려하세요."),
 ("tristan","트리스탄","Tristan","SR","불","버스터","한손검","버스터 / 공격", "스토리 초반 폭발 피해를 보완합니다."),
]
WEAPONS = [
 ("gluttonous-soul-gauntlets","영혼의 탐식 건틀릿","Gauntlets","SSR","데리엘리","공격력 · 치명타", "공식/커뮤니티 DB 검증"),
 ("lichdragons-roar","리치드래곤의 포효","Two-hand Sword","SSR","에스카노르","공격력 · 궁극기 피해", "공식/커뮤니티 DB 검증"),
 ("black-flame-wings","검은 화염의 날개","Dual Swords","SSR","멜리오다스","공격력 · 치명타", "공식/커뮤니티 DB 검증"),
 ("crimson-flame-tome","진홍 불꽃의 마도서","Book","SSR","고서","원소 피해 · 버스트", "공식/커뮤니티 DB 검증"),
 ("shadow-rupture-grimoire","그림자 파열의 마도서","Book","SSR","엘리자베스","체력 · 파티 지원", "공식/커뮤니티 DB 검증"),
]
ITEMS = [
 ("star-fragment","별의 파편","강화 재료","탐험·이벤트·보상", "장비와 성장 시스템에 사용되는 재료입니다."),
 ("cube-key","큐브 열쇠","콘텐츠 재료","시간의 틈·콘텐츠 보상", "콘텐츠 입장/보상 관련 재료입니다."),
 ("dragonblood-stone","드래곤블러드 스톤","성장 재료","필드 탐험·보스 보상", "성장 및 제작 관련 재료입니다."),
 ("ghost-guppy","유령구피","낚시","낚시 지역", "낚시 도감 및 제작 용도를 게임 내 최신 데이터로 확인하세요."),
]

@contextmanager
def connect():
    con = sqlite3.connect(DATABASE_PATH)
    con.row_factory = sqlite3.Row
    try: yield con
    finally: con.close()

def initialize():
    with connect() as c:
        c.executescript('''
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS characters(id TEXT PRIMARY KEY, name_ko TEXT, name_en TEXT, rarity TEXT, element TEXT, role TEXT, weapon_type TEXT, roles TEXT, guide TEXT, source_url TEXT, confidence TEXT);
        CREATE TABLE IF NOT EXISTS weapons(id TEXT PRIMARY KEY, name_ko TEXT, weapon_type TEXT, rarity TEXT, recommended_character TEXT, stats TEXT, confidence TEXT);
        CREATE TABLE IF NOT EXISTS items(id TEXT PRIMARY KEY, name_ko TEXT, item_type TEXT, obtain TEXT, description TEXT);
        CREATE TABLE IF NOT EXISTS catalog(id TEXT PRIMARY KEY, category TEXT NOT NULL, slug TEXT NOT NULL, name_ko TEXT NOT NULL, name_en TEXT, description_ko TEXT, description_en TEXT, source_url TEXT, image_url TEXT, confidence TEXT);
        CREATE TABLE IF NOT EXISTS map_markers(id TEXT PRIMARY KEY, game_id TEXT, marker_type TEXT, name_ko TEXT, name_en TEXT, description_ko TEXT, latitude REAL, longitude REAL, region TEXT, icon_url TEXT, raw_json TEXT);
        CREATE INDEX IF NOT EXISTS idx_catalog_category ON catalog(category);
        CREATE INDEX IF NOT EXISTS idx_catalog_name_ko ON catalog(name_ko);
        CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, uid TEXT, region TEXT DEFAULT 'Global', star_book INTEGER DEFAULT 1, world_level INTEGER DEFAULT 1, story_progress TEXT DEFAULT '', created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS owned_characters(account_id INTEGER, character_id TEXT, level INTEGER DEFAULT 1, weapon_name TEXT DEFAULT '', favorite INTEGER DEFAULT 0, PRIMARY KEY(account_id,character_id), FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE, FOREIGN KEY(character_id) REFERENCES characters(id));
        CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, character_id TEXT, note TEXT NOT NULL, done INTEGER DEFAULT 0, FOREIGN KEY(account_id) REFERENCES accounts(id) ON DELETE CASCADE);
        ''')
        owned_cols={r[1] for r in c.execute('PRAGMA table_info(owned_characters)')}
        for name,definition in [('breakthrough','INTEGER DEFAULT 0'),('mastery','INTEGER DEFAULT 0'),('combat_power','INTEGER DEFAULT 0'),('equipment_note',"TEXT DEFAULT ''")]:
            if name not in owned_cols:c.execute(f'ALTER TABLE owned_characters ADD COLUMN {name} {definition}')
        if not c.execute('SELECT 1 FROM characters LIMIT 1').fetchone():
            c.executemany('INSERT INTO characters VALUES(?,?,?,?,?,?,?,?,?,?,?)', [x+("https://7dsorigin.app/en/characters", "community_verified") for x in CHARACTERS])
            c.executemany('INSERT INTO weapons VALUES(?,?,?,?,?,?,?)', WEAPONS)
            c.executemany('INSERT INTO items VALUES(?,?,?,?,?)', ITEMS)
        catalog_path=USER_DIR/'catalog.json' if (USER_DIR/'catalog.json').exists() else BASE_DIR/'data'/'catalog.json'
        if catalog_path.exists():
            payload=json.loads(catalog_path.read_text(encoding='utf-8'))
            rows=[(r['id'],r['category'],r['slug'],r['name_ko'],r['name_en'],r.get('description_ko',''),r.get('description_en',''),r['source_url'],r.get('image_url',''),r.get('confidence','authorized_public_page')) for r in payload.get('records',[])]
            c.executemany('INSERT INTO catalog VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name_ko=excluded.name_ko,name_en=excluded.name_en,description_ko=excluded.description_ko,description_en=excluded.description_en,source_url=excluded.source_url,image_url=excluded.image_url,confidence=excluded.confidence',rows)
        map_path=BASE_DIR/'data'/'map_markers.json'
        if map_path.exists() and not c.execute('SELECT 1 FROM map_markers LIMIT 1').fetchone():
            markers=json.loads(map_path.read_text(encoding='utf-8')).get('markers',[])
            rows=[(m['id'],m.get('gameId'),m.get('markerType',''),m.get('nameKo') or m.get('nameEn') or m.get('markerType',''),m.get('nameEn',''),m.get('descriptionKo',''),m.get('lat'),m.get('lng'),m.get('region',''),m.get('iconUrl',''),json.dumps(m,ensure_ascii=False)) for m in markers]
            c.executemany('INSERT OR REPLACE INTO map_markers VALUES(?,?,?,?,?,?,?,?,?,?,?)',rows)
        c.execute("INSERT OR REPLACE INTO metadata VALUES('game_version',?)", (DATA_VERSION,))
        c.execute("INSERT OR REPLACE INTO metadata VALUES('last_verified',?)", (date.today().isoformat(),))
        c.commit()

def search(query, kind="all"):
    q=f"%{query.strip()}%"
    with connect() as c:
        out=[]
        if kind in ('all','characters'):
            out += [("캐릭터", r['name_ko'], r['id'], f"{r['rarity']} · {r['element']} · {r['roles']}") for r in c.execute('SELECT * FROM characters WHERE name_ko LIKE ? OR name_en LIKE ? ORDER BY rarity DESC,name_ko',(q,q))]
        if kind in ('all','weapons'):
            out += [("무기", r['name_ko'], r['id'], f"{r['rarity']} · {r['weapon_type']} · {r['recommended_character']}") for r in c.execute('SELECT * FROM weapons WHERE name_ko LIKE ?',(q,))]
        if kind in ('all','items'):
            out += [("아이템", r['name_ko'], r['id'], f"{r['item_type']} · {r['obtain']}") for r in c.execute('SELECT * FROM items WHERE name_ko LIKE ?',(q,))]
        if kind in ('all','catalog'):
            labels={'weapons':'무기','armor':'방어구','accessories':'장신구','items':'아이템','pets':'펫','monsters':'몬스터','elite-monsters':'정예 몬스터','field-bosses':'필드 보스','effects':'효과','characters':'캐릭터'}
            out += [(labels.get(r['category'],r['category']),r['name_ko'],r['id'],(r['description_ko'] or r['description_en'])[:150]) for r in c.execute('SELECT * FROM catalog WHERE name_ko LIKE ? OR name_en LIKE ? ORDER BY category,name_ko LIMIT 250',(q,q))]
        return out

def characters():
    with connect() as c: return c.execute('SELECT * FROM characters ORDER BY CASE rarity WHEN "SSR" THEN 0 ELSE 1 END, name_ko').fetchall()
def character(cid):
    with connect() as c: return c.execute('SELECT * FROM characters WHERE id=?',(cid,)).fetchone()
def character_details(cid):
    row=character(cid)
    path=BASE_DIR/'data'/'character_details.json'
    if not row or not path.exists():return {}
    payload=json.loads(path.read_text(encoding='utf-8')).get('characters',{})
    for detail in payload.values():
        if detail.get('name_en','').lower()==row['name_en'].lower():return detail
    return {}
def catalog_entry(entity_id):
    with connect() as c:return c.execute('SELECT * FROM catalog WHERE id=?',(entity_id,)).fetchone()
def map_search(query='',marker_type='all',limit=500):
    q=f"%{query.strip()}%"
    with connect() as c:
        if marker_type=='all':return c.execute('SELECT * FROM map_markers WHERE name_ko LIKE ? OR name_en LIKE ? ORDER BY marker_type,name_ko LIMIT ?',(q,q,limit)).fetchall()
        return c.execute('SELECT * FROM map_markers WHERE marker_type=? AND (name_ko LIKE ? OR name_en LIKE ?) ORDER BY name_ko LIMIT ?',(marker_type,q,q,limit)).fetchall()
def map_types():
    with connect() as c:return [r[0] for r in c.execute('SELECT DISTINCT marker_type FROM map_markers ORDER BY marker_type')]
def account_list():
    with connect() as c: return c.execute('SELECT * FROM accounts ORDER BY id DESC').fetchall()
def account(aid):
    with connect() as c:return c.execute('SELECT * FROM accounts WHERE id=?',(aid,)).fetchone()
def create_account(name,uid,region,star,world,story):
    with connect() as c:
        c.execute('INSERT INTO accounts(name,uid,region,star_book,world_level,story_progress,created_at) VALUES(?,?,?,?,?,?,?)',(name,uid,region,star,world,story,date.today().isoformat())); c.commit()
def delete_account(aid):
    with connect() as c: c.execute('DELETE FROM accounts WHERE id=?',(aid,)); c.commit()
def owned(aid):
    with connect() as c: return c.execute('SELECT c.*,o.level,o.weapon_name,o.breakthrough,o.mastery,o.combat_power,o.equipment_note FROM owned_characters o JOIN characters c ON c.id=o.character_id WHERE o.account_id=?',(aid,)).fetchall()
def set_owned(aid,cid,level=1,weapon='',breakthrough=0,mastery=0,combat_power=0,equipment_note=''):
    with connect() as c: c.execute('INSERT INTO owned_characters(account_id,character_id,level,weapon_name,breakthrough,mastery,combat_power,equipment_note) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(account_id,character_id) DO UPDATE SET level=excluded.level,weapon_name=excluded.weapon_name,breakthrough=excluded.breakthrough,mastery=excluded.mastery,combat_power=excluded.combat_power,equipment_note=excluded.equipment_note',(aid,cid,level,weapon,breakthrough,mastery,combat_power,equipment_note)); c.commit()
def remove_owned(aid,cid):
    with connect() as c: c.execute('DELETE FROM owned_characters WHERE account_id=? AND character_id=?',(aid,cid));c.commit()
