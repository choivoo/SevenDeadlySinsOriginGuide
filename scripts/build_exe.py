"""Repeatable Windows onedir build."""
from pathlib import Path
import subprocess,sys,shutil,json
import hashlib,zipfile
root=Path(__file__).resolve().parents[1]
out=root/'Release'; staging=root/'release_staging'
for path in (out,staging):
    if path.exists(): shutil.rmtree(path)
cmd=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--windowed','--name','SevenDeadlySinsOriginGuide','--paths',str(root),'--distpath',str(staging),'--workpath',str(root/'build'),'--specpath',str(root),'--collect-all','rapidocr_onnxruntime']
if (root/'data'/'catalog.json').exists():cmd += ['--add-data',f"{root/'data'/'catalog.json'};data"]
if (root/'data'/'map_markers.json').exists():cmd += ['--add-data',f"{root/'data'/'map_markers.json'};data"]
if (root/'data'/'character_details.json').exists():cmd += ['--add-data',f"{root/'data'/'character_details.json'};data"]
cmd += [str(root/'app'/'main.py')]
subprocess.run(cmd,check=True,cwd=root)
out.mkdir(); dist=staging/'SevenDeadlySinsOriginGuide'
for child in dist.iterdir(): shutil.move(str(child),out/child.name)
shutil.rmtree(staging)
(out/'README.txt').write_text('일곱 개의 대죄 Origin 완전 공략\n\nSevenDeadlySinsOriginGuide.exe를 실행하세요.\n내 계정에서 계정을 등록한 뒤 캐릭터 DB에서 보유 영웅을 추가하면 성장 추천을 사용할 수 있습니다.\nUID 자동 동기화는 공식 공개 API가 확인되지 않아 제공하지 않습니다.\n',encoding='utf-8')
(out/'DATA_SOURCES.txt').write_text('Official: https://7origin.netmarble.com/\nCommunity database: https://7dsorigin.app/en\nData version: 1.8\n',encoding='utf-8')
(out/'source_manifest.json').write_text(json.dumps({'game_version':'1.8','data_version':'1.0.0','sources':['https://7origin.netmarble.com/','https://7dsorigin.app/en'],'entity_counts':{'characters':25,'weapons':5,'items':4}},ensure_ascii=False,indent=2),encoding='utf-8')
(out/'LICENSES.txt').write_text('PySide6 / Qt and Python component licenses apply. This is an unofficial fan project.',encoding='utf-8')
portable=root/'SevenDeadlySinsOriginGuide_Portable.zip'
if portable.exists(): portable.unlink()
with zipfile.ZipFile(portable,'w',zipfile.ZIP_DEFLATED) as archive:
    for file in out.rglob('*'):
        if file.is_file(): archive.write(file,file.relative_to(out.parent))
digest=hashlib.sha256(portable.read_bytes()).hexdigest()
(root/'SevenDeadlySinsOriginGuide_Portable.zip.sha256').write_text(f'{digest}  {portable.name}\n',encoding='ascii')
print(out)
