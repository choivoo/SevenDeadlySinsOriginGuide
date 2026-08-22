import json, shutil, sqlite3
from datetime import datetime
from pathlib import Path
from app.config import DATABASE_PATH, USER_DIR, DATA_VERSION

def validate_database(path=DATABASE_PATH):
    problems=[]
    if not Path(path).exists(): return ["데이터베이스 파일이 없습니다."]
    try:
        con=sqlite3.connect(path)
        integrity=con.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity!="ok": problems.append(f"SQLite integrity: {integrity}")
        for table in ("characters","weapons","items","accounts","owned_characters"):
            if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",(table,)).fetchone(): problems.append(f"필수 테이블 누락: {table}")
        if not problems and con.execute("SELECT COUNT(*) FROM characters").fetchone()[0]<25: problems.append("캐릭터 데이터가 예상보다 적습니다.")
        con.close()
    except Exception as exc: problems.append(str(exc))
    return problems

def backup_database():
    folder=USER_DIR/"backups"; folder.mkdir(exist_ok=True)
    target=folder/f"game-{datetime.now():%Y%m%d-%H%M%S}.db"
    shutil.copy2(DATABASE_PATH,target)
    return target

def data_status():
    con=sqlite3.connect(DATABASE_PATH)
    counts={name:con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] for name in ("characters","weapons","items","catalog","map_markers")}
    con.close()
    return {"game_version":DATA_VERSION,"counts":counts,"validation":validate_database()}

