import traceback
import requests
from flask import Response
from .setup import P

def proxy_m3u(user_id, req):
    try:
        # 1. DB(설정화면)에서 사용자가 입력한 매핑 정보 가져오기
        mapping_str = P.ModelSetting.get("id_mapping")
        mappings = {}
        if mapping_str:
            for line in mapping_str.split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    mappings[k.strip()] = v.strip()
        
        # 2. ID 확인 및 API 키 추출
        if user_id not in mappings:
            P.logger.warning(f"[addrhide] 등록되지 않은 ID 접근: {user_id}")
            return Response("권한이 없거나 등록되지 않은 ID입니다.", status=403)
        
        api_key = mappings[user_id]
        
        # 3. 로컬 내부망에서 원본 서버로 요청 (속도 최적화)
        target_url = f"http://127.0.0.1:9999/alive/api/m3uall?apikey={api_key}"
        
        # 4. 데이터 받아와서 사용자에게 전달
        res = requests.get(target_url, timeout=10)
        res.raise_for_status() 
        
        return Response(res.text, mimetype='application/x-mpegurl')

    except Exception as e:
        P.logger.error(f"[addrhide] Proxy Error: {e}")
        P.logger.error(traceback.format_exc())
        return Response("데이터를 불러오는 중 오류가 발생했습니다.", status=500)
