import traceback
import requests
from flask import Response, abort, render_template
from . import blueprint

# 1. ID별 API 키 매핑 (여기에 원하는 ID와 실제 API 키를 설정하세요)
API_KEY_MAP = {
    "my_id": "여기에_실제_API키를_입력하세요",
    "family": "가족용_API키를_입력하세요",
    "friend": "친구용_API키를_입력하세요"
}

# 2. 기본 페이지 (http://서버주소:9999/addrhide/ 로 접속 시 화면)
@blueprint.route('/', methods=['GET'])
def index():
    return render_template('addrhide_main.html')

# 3. 핵심 프록시 기능 (http://서버주소:9999/addrhide/<user_id> 로 접속 시)
@blueprint.route('/<user_id>', methods=['GET'])
def proxy_m3u(user_id):
    try:
        # 설정된 ID가 아니면 403 (권한 없음) 에러 발생
        if user_id not in API_KEY_MAP:
            abort(403) 
        
        api_key = API_KEY_MAP[user_id]
        
        # 서버 내부망(127.0.0.1)에서 원본 주소로 API 요청
        target_url = f"http://127.0.0.1:9999/alive/api/m3uall?apikey={api_key}"
        
        # 데이터 가져오기 (타임아웃 10초 설정)
        res = requests.get(target_url, timeout=10)
        res.raise_for_status() # 통신 에러 시 예외 처리
        
        # M3U 포맷 그대로 클라이언트(사용자)에게 전달
        return Response(res.text, mimetype='application/x-mpegurl')

    except Exception as e:
        print(f"[addrhide] Proxy Error: {e}")
        print(traceback.format_exc())
        return Response("데이터를 불러오는 중 오류가 발생했습니다.", status=500)
