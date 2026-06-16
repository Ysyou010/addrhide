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
        
        target_url = mappings[user_id]
        base_url = req.url_root.rstrip('/')
        is_local_call = False
        
        if target_url.startswith(base_url):
            target_url = target_url.replace(base_url, "http://127.0.0.1:9999")
            is_local_call = True
        
        headers = {
            'User-Agent': req.headers.get('User-Agent', 'Mozilla/5.0'),
            'Host': req.host
        }
        
        res = requests.get(target_url, headers=headers, timeout=20)
        res.raise_for_status() 
        
        res_text = res.text
        
        if is_local_call:
            res_text = res_text.replace("http://127.0.0.1:9999", base_url)
            
        # 🌟 핵심 방어벽: M3U 텍스트 안에 있는 alive의 라이선스 요청 주소를 addrhide의 주소로 싹 바꿔치기합니다.
        res_text = res_text.replace("/alive/proxy/license", f"/{P.package_name}/normal/license")
        
        return Response(res_text, mimetype='application/x-mpegurl')

    except Exception as e:
        P.logger.error(f"[addrhide] Proxy Error: {e}")
        P.logger.error(traceback.format_exc())
        error_msg = f"데이터를 불러오는 중 오류가 발생했습니다.<br><br>시도한 주소: {target_url}<br>에러 원인: {str(e)}"
        return Response(error_msg, status=500)


# 🌟 찾아내신 alive의 DRM 라이선스 프록시 코드를 addrhide 규격에 맞게 이식
def license_proxy(req):
    try:
        # Host 헤더를 제외한 모든 헤더 복사
        headers = {k: v for k, v in req.headers.items() if k.lower() != "host"}
        
        # alive 플러그인의 특수 헤더 규칙 적용
        if "Real-Origin" in headers:
            headers["Origin"] = headers.pop("Real-Origin")
        if "Real-Referer" in headers:
            headers["Referer"] = headers.pop("Real-Referer")
            
        url = headers.pop("Real-Url", None)
        if not url:
            return Response("Missing Real-Url", status=400)

        # 원본 DRM 서버(Wavve, Tving 등)에 라이선스 키 요청
        res = requests.request(
            method=req.method,
            url=url,
            headers=headers,
            data=req.get_data(),
            cookies=req.cookies,
            allow_redirects=False,
            timeout=10,
        )
        
        # 불필요한 전송용 헤더 제거
        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]
        resp_headers = [(k, v) for k, v in res.raw.headers.items() if k.lower() not in excluded_headers]
        
        # 성공적으로 받아온 암호 해독 키를 플레이어에 반환!
        return Response(res.content, res.status_code, resp_headers)
        
    except Exception as e:
        P.logger.error(f"[addrhide] License Proxy Error: {e}")
        P.logger.error(traceback.format_exc())
        return Response("License Proxy Error", status=500)
