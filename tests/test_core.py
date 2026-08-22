import tempfile
from pathlib import Path
from app import database as db
from app.recommendations import analyze
from app.maintenance import validate_database

def test_seed_and_search(monkeypatch):
    p=Path(tempfile.mkdtemp())/'game.db';monkeypatch.setattr(db,'DATABASE_PATH',p);db.initialize()
    assert len(db.characters()) == 25
    assert any(x[1]=='데리엘리' for x in db.search('데리엘리'))
def test_account_recommendation(monkeypatch):
    p=Path(tempfile.mkdtemp())/'game.db';monkeypatch.setattr(db,'DATABASE_PATH',p);db.initialize();db.create_account('Test','','Global',1,1,'')
    aid=db.account_list()[0]['id'];db.set_owned(aid,'meliodas',20,'검은 화염의 날개')
    assert analyze(aid)['score']>0

def test_database_validation(monkeypatch):
    p=Path(tempfile.mkdtemp())/'game.db';monkeypatch.setattr(db,'DATABASE_PATH',p);db.initialize()
    assert validate_database(p)==[]

