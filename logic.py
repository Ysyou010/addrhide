import traceback
import requests
from urllib.parse import urlparse
from flask import Response, stream_with_context
from plugin import F  # ★ 프레임워크 전역 객체(F) 가져오기
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
        
        parsed_url = urlparse(target_url)
        path_parts = parsed_url.path.strip('/').split('/')
        origin_plugin = path_parts[0] if path_parts else "alive"
        
        # ★ F 객체를 통해 안전하게 DDNS를 가져옵니다.
        sys_ddns = F.SystemModelSetting.get('ddns')
        base_url = sys_ddns.rstrip('/') if sys_ddns else req.url_root.rstrip('/')
        
        local_port = req.environ.get('SERVER_PORT', '9999')
        local_url = f"http://127.0.0.1:{local_port}"
        
        fetch_url = target_url
        if target_url.startswith(base_url):
            fetch_url = target_url.replace(base_url, local_url)
            
        headers = {'User-Agent': req.headers.get('User-Agent', 'Mozilla/5.0'), 'Host': req.host}
        res = requests.get(fetch_url, headers=headers, timeout=20)
        res.raise_for_status()
        
        res_text = res.text
        
        tmp_marker = "__ADDRHIDE_MARKER__"
        res_text = res_text.replace(f"{base_url}/{origin_plugin}/", tmp_marker)
        res_text = res_text.replace(f"{local_url}/{origin_plugin}/", tmp_marker)
        res_text = res_text.replace(f"/{origin_plugin}/", tmp_marker)
        
        final_route = f"{base_url}/{P.package_name}/fx/route/{origin_plugin}/"
        res_text = res_text.replace(tmp_marker, final_route)
        
        return Response(res_text, mimetype='application/x-mpegurl')

    except Exception as e:
        P.logger.error(f"[addrhide] Proxy M3U Error: {e}")
        P.logger.error(traceback.format_exc())
        return Response(f"에러 발생<br>주소: {target_url}<br>원인: {e}", status=500)

def universal_route(target_path, req):
    try:
        local_port = req.environ.get('SERVER_PORT', '9999')
        url = f"http://127.0.0.1:{local_port}{target_path}"
        
        if req.query_string:
            url += f"?{req.query_string.decode('utf-8')}"
            
        req_headers = {k: v for k, v in req.headers.items() if k.lower() not in ['host', 'content-length']}
        
        res = requests.request(
            method=req.method,
            url=url,
            headers=req_headers,
            data=req.get_data(),
            cookies=req.cookies,
            allow_redirects=False,
            stream=True,  
            timeout=30
        )
        
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp_headers = [(k, v) for k, v in res.raw.headers.items() if k.lower() not in excluded_headers]
        
        return Response(
            stream_with_context(res.iter_content(chunk_size=1048576)), 
            status=res.status_code, 
            headers=resp_headers, 
            content_type=res.headers.get('Content-Type')
        )
        
    except Exception as e:
        P.logger.error(f"[addrhide] Universal Route Error: {e}")
        P.logger.error(traceback.format_exc())
        return Response("재생 중계 오류", status=500)
        if target_url.startswith(base_url):
            fetch_url = target_url.replace(base_url, local_url)
            
        headers = {'User-Agent': req.headers.get('User-Agent', 'Mozilla/5.0'), 'Host': req.host}
        res = requests.get(fetch_url, headers=headers, timeout=20)
        res.raise_for_status()
        
        res_text = res.text
        
        tmp_marker = "__ADDRHIDE_MARKER__"
        res_text = res_text.replace(f"{base_url}/{origin_plugin}/", tmp_marker)
        res_text = res_text.replace(f"{local_url}/{origin_plugin}/", tmp_marker)
        res_text = res_text.replace(f"/{origin_plugin}/", tmp_marker)
        
        final_route = f"{base_url}/{P.package_name}/fx/route/{origin_plugin}/"
        res_text = res_text.replace(tmp_marker, final_route)
        
        return Response(res_text, mimetype='application/x-mpegurl')

    except Exception as e:
        P.logger.error(f"[addrhide] Proxy M3U Error: {e}")
        P.logger.error(traceback.format_exc())
        return Response(f"에러 발생<br>주소: {target_url}<br>원인: {e}", status=500)

# 2. 영상 재생, 구간 탐색(Range), DRM 라이선스를 완벽하게 중계하는 함수
def universal_route(req):
    try:
        if "/route" not in req.path:
            return Response("잘못된 라우트 경로", status=400)
            
        target_path = req.path.split("/route", 1)[1]
        
        local_port = req.environ.get('SERVER_PORT', '9999')
        url = f"http://127.0.0.1:{local_port}{target_path}"
        
        if req.query_string:
            url += f"?{req.query_string.decode('utf-8')}"
            
        # Host만 제거하고 Range(구간탐색) 등 중요한 헤더는 모두 보존
        req_headers = {k: v for k, v in req.headers.items() if k.lower() not in ['host']}
        
        res = requests.request(
            method=req.method,
            url=url,
            headers=req_headers,
            data=req.get_data(),
            cookies=req.cookies,
            allow_redirects=False,
            stream=True,  
            timeout=30
        )
        
        # 로컬 영상의 Content-Length를 살리기 위해 전송 방식 관련 헤더만 신중하게 제거
        excluded_headers = ['content-encoding', 'transfer-encoding', 'connection', 'keep-alive', 'proxy-authenticate', 'te', 'trailers', 'upgrade']
        resp_headers = [(k, v) for k, v in res.raw.headers.items() if k.lower() not in excluded_headers]
        
        return Response(
            stream_with_context(res.iter_content(chunk_size=1048576)), 
            status=res.status_code, 
            headers=resp_headers
        )
        
    except Exception as e:
        P.logger.error(f"[addrhide] Universal Route Error: {e}")
        P.logger.error(traceback.format_exc())
        return Response("재생 중계 오류", status=500)
