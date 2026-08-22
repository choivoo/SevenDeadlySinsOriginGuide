from app.database import owned,account

ROLE_SCORE={"공격":3,"버스터":3,"지원":2,"수호":2}
def analyze(account_id):
    heroes=owned(account_id)
    if not heroes:
        return {"score":0,"headline":"보유 영웅을 등록해 주세요", "body":"내 계정 탭에서 캐릭터를 추가하면 보유 데이터 기반 성장 우선순위와 파티를 계산합니다.","team":[],"tasks":["주력으로 사용할 공격형 영웅 1명을 등록하세요.","지원 또는 수호 역할 영웅을 1명 추가하세요."]}
    profile=account(account_id);ranked=[]
    for h in heroes:
        score=ROLE_SCORE.get(h['role'],1)*20 + min(h['level'],90)*0.7 + (15 if h['rarity']=='SSR' else 5) + (8 if h['weapon_name'] else 0) + min(h['mastery'],100)*.15 + min(h['breakthrough'],6)*2 + min(h['combat_power'],100000)/10000
        ranked.append((score,h))
    ranked.sort(reverse=True,key=lambda x:x[0])
    team=[x[1] for x in ranked[:3]]
    missing=[]
    roles=" ".join(h['roles'] for _,h in ranked)
    if '지원' not in roles: missing.append('지원 역할 영웅이 부족합니다.')
    if '수호' not in roles: missing.append('수호 역할 영웅이 부족합니다.')
    main=ranked[0][1]
    tasks=[f"{main['name_ko']} 레벨·마스터리·핵심 무기를 우선 강화하세요."]
    if not main['weapon_name']: tasks.append(f"{main['name_ko']}에 맞는 {main['weapon_type']} 계열 무기를 등록하고 제작 재료를 확인하세요.")
    tasks += missing or ["현재 역할 구성이 균형적입니다. 주력 3인의 장비 강화를 진행하세요."]
    if profile and profile['world_level']>max(h['level'] for _,h in ranked)//10:tasks.append('월드 레벨 대비 주력 캐릭터 레벨이 낮습니다. 경험치와 돌파 재료를 먼저 확보하세요.')
    setting=f"주력 {main['name_ko']}: {main['weapon_name'] or main['weapon_type']+' 계열 무기'} / {main['role']} 중심 공격 세팅"
    return {"score":round(sum(x[0] for x in ranked)/len(ranked),1), "headline":f"{main['name_ko']} 중심 성장 계획", "body":f"별의 서 {profile['star_book'] if profile else '-'} · 월드 {profile['world_level'] if profile else '-'} · 스토리 {profile['story_progress'] if profile else '-'}와 보유 영웅의 레벨, 돌파, 마스터리, 전투력, 무기 및 역할 균형으로 계산한 로컬 추천입니다.", "team":team, "tasks":tasks,"setting":setting}

