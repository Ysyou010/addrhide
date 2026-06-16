import traceback
import requests
from flask import Response
from .setup import P

def proxy_m3u(user_id, req):
    target_url = "알 수 없는 주소"
    try:
        # 1. 설정창에서 입력한 매핑 정보 불러오기
        mapping_str = P.ModelSetting.get("id_mapping")
        mappings = {}
        if mapping_str:
            for line in mapping_str.split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    mappings[k.strip()] = v.strip()
        
        if user_id not in mappings:
            return Response("권한이 없거나 등록되지 않은 ID입니다.", status=403)
        
        # 2. API키만 가져오는 것이 아니라, 입력한 전체 주소를 그대로 가져옵니다.
        target_url = mappings[user_id]
        
        # 3. 네트워크 통신 오류 방지 (외부 IP로 들어왔어도 서버 내부 127.0.0.1 통신으로 강제 변환)
        base_url = req.url_root.rstrip('/')
        if target_url.startswith(base_url):
            target_url = target_url.replace(base_url, "http://127.0.0.1:9999")
        
        # 4. 데이터 요청
        headers = {'User-Agent': req.headers.get('User-Agent', 'Mozilla/5.0')}
        res = requests.get(target_url, headers=headers, timeout=20)
        res.raise_for_status() 
        
        return Response(res.text, mimetype='application/x-mpegurl')

    except Exception as e:
        P.logger.error(f"[addrhide] Proxy Error: {e}")
        P.logger.error(traceback.format_exc())
        
        error_msg = f"데이터를 불러오는 중 오류가 발생했습니다.<br><br>시도한 주소: {target_url}<br>에러 원인: {str(e)}"
        return Response(error_msg, status=500)
