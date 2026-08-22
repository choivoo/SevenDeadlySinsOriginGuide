# 일곱 개의 대죄 Origin 완전 공략

비공식 Windows 팬 컴패니언 앱입니다. 캐릭터 검색, 로컬 계정 관리, 보유 영웅 기반 성장 추천을 인터넷 없이 사용할 수 있습니다.

## 실행

GitHub Releases에서 `SevenDeadlySinsOriginGuide_Portable.zip`을 내려받고 압축을 푼 뒤 `SevenDeadlySinsOriginGuide.exe`를 실행합니다. `_internal` 폴더는 EXE와 같은 위치에 두어야 합니다.

## 개인정보와 계정

비밀번호, 인증번호, 세션 쿠키 또는 로그인 토큰을 요구하지 않습니다. 공식 공개 API가 확인되지 않은 UID 전체 자동 동기화는 지원하지 않습니다. 사용자가 입력한 데이터는 `%USERPROFILE%\7DSOriginCompleteGuide\game.db`에만 저장됩니다.

## 데이터 출처

- 공식: https://7origin.netmarble.com/
- 공개 커뮤니티 DB: https://7dsorigin.app/en

앱은 Netmarble의 공식 프로그램이 아닙니다. 게임 관련 권리는 각 권리자에게 있습니다.

## 개발 빌드

Python 3.11 이상에서 `pip install -r requirements.txt`, `pytest -q`, `python scripts/build_exe.py` 순서로 빌드합니다.

