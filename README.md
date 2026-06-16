# AddrHide 플러그인

API 키와 원본 경로를 숨기고 우회 접속을 지원하는 리버스 프록시 플러그인입니다.

## 기능
- `http://.../alive/api/m3uall?apikey=XXX` 구조를 숨김
- `http://.../addrhide/[ID]` 형태로 간소화 및 보안 강화

## 설정 방법
1. `logic.py` 파일의 `API_KEY_MAP` 딕셔너리에 원하는 `ID`와 `실제 API 키`를 매핑합니다.
2. 서버를 재시작하거나 플러그인을 다시 로드합니다.
3. 플레이어에 `http://www.ysyou0109.win:9999/addrhide/설정한ID` 를 입력하여 사용합니다.
