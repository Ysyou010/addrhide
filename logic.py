import traceback
import requests
from flask import Response
from .setup import P

def proxy_m3u(user_id, req):
    target_url = "알 수 없는 주소"
    try:
        mapping_str = P.ModelSetting.get("id_mapping")
        mappings = {}
        if mapping_str:
            for line in mapping_str.split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    mappings[k.strip()] = v.strip()
        
        if user_id not in mappings:
            return Response("권한이 없거나 등록되지 않은 ID입니다.", status=403)
        
        api_key = mappings[user_id]
        
        # 1. 도커 내부 루프백 문제를 피하기 위해 클라이언트가 접속한 기본 주소를 동적으로 가져옵니다.
        base_url = req.url_root.rstrip('/')
        target_url = f"{base_url}/alive/api/m3uall?apikey={api_key}"
        
        # 2. 서버 통신 타임아웃을 넉넉히(20초) 잡고, 정상적인 접근인 것처럼 헤더를 설정합니다.
        headers = {'User-Agent': req.headers.get('User-Agent', 'Mozilla/5.0')}
        res = requests.get(target_url, headers=headers, timeout=20)
        res.raise_for_status() 
        
        return Response(res.text, mimetype='application/x-mpegurl')

    except Exception as e:
        P.logger.error(f"[addrhide] Proxy Error: {e}")
        P.logger.error(traceback.format_exc())
        
        # 3. 스마트폰이나 PC의 브라우저 화면에 정확한 에러 원인과 주소를 출력하여 디버깅을 돕습니다.
        error_msg = f"데이터를 불러오는 중 오류가 발생했습니다.<br><br>시도한 주소: {target_url}<br>에러 원인: {str(e)}"
        return Response(error_msg, status=500)
