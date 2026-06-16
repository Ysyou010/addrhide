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
        
        target_url = mappings[user_id]
        
        # 2. 클라이언트의 실제 외부 주소(예: http://140.238.4.62:9999)
        base_url = req.url_root.rstrip('/')
        is_local_call = False
        
        # 3. 내부 통신으로 변환 (서버 부하 및 네트워크 오류 방지)
        if target_url.startswith(base_url):
            target_url = target_url.replace(base_url, "http://127.0.0.1:9999")
            is_local_call = True
        
        # 4. 🌟 핵심: 원본 서버에 요청할 때, 내가 127.0.0.1이 아니라 '외부 주소'인 척 Host 헤더를 넘겨줍니다.
        headers = {
            'User-Agent': req.headers.get('User-Agent', 'Mozilla/5.0'),
            'Host': req.host
        }
        
        res = requests.get(target_url, headers=headers, timeout=20)
        res.raise_for_status() 
        
        res_text = res.text
        
        # 5. 🌟 2차 방어: 혹시라도 M3U 파일 안에 127.0.0.1로 적힌 영상 주소가 있다면 외부 주소로 강제 치환!
        if is_local_call:
            res_text = res_text.replace("http://127.0.0.1:9999", base_url)
        
        return Response(res_text, mimetype='application/x-mpegurl')

    except Exception as e:
        P.logger.error(f"[addrhide] Proxy Error: {e}")
        P.logger.error(traceback.format_exc())
        
        error_msg = f"데이터를 불러오는 중 오류가 발생했습니다.<br><br>시도한 주소: {target_url}<br>에러 원인: {str(e)}"
        return Response(error_msg, status=500)
