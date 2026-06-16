import traceback
import requests
from urllib.parse import urlparse
from flask import Response, stream_with_context
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
        
        # 원본 플러그인 이름 추출 (예: alive, ff_local_m3u 등)
        parsed_url = urlparse(target_url)
        path_parts = parsed_url.path.strip('/').split('/')
        origin_plugin = path_parts[0] if path_parts else "alive"
        
        base_url = req.url_root.rstrip('/')
        local_port = req.environ.get('SERVER_PORT', '9999')
        local_url = f"http://127.0.0.1:{local_port}"
        
        # 내부망 통신으로 최적화하여 M3U 텍스트 가져오기
        fetch_url = target_url
        if target_url.startswith(base_url):
            fetch_url = target_url.replace(base_url, local_url)
            
        headers = {'User-Agent': req.headers.get('User-Agent', 'Mozilla/5.0'), 'Host': req.host}
        res = requests.get(fetch_url, headers=headers, timeout=20)
        res.raise_for_status()
        
        res_text = res.text
        
        # 🌟 [핵심] M3U 파일 안에 있는 원본 플러그인 주소(alive, ff_local_m3u)를 모두 addrhide 라우터로 치환
        tmp_marker = "__ADDRHIDE_ROUTE_MARKER__"
        res_text = res_text.replace(f"{base_url}/{origin_plugin}/", f"{tmp_marker}/")
        res_text = res_text.replace(f"{local_url}/{origin_plugin}/", f"{tmp_marker}/")
        res_text = res_text.replace(f"/{origin_plugin}/", f"{tmp_marker}/")
        
        final_route = f"{base_url}/{P.package_name}/normal/route/{origin_plugin}"
        res_text = res_text.replace(tmp_marker, final_route)
        
        return Response(res_text, mimetype='application/x-mpegurl')

    except Exception as e:
        P.logger.error(f"[addrhide] Proxy M3U Error: {e}")
        P.logger.error(traceback.format_exc())
        return Response(f"데이터를 불러오는 중 오류가 발생했습니다.<br>시도한 주소: {target_url}<br>원인: {e}", status=500)


def universal_route(target_path, req):
    """
    플레이어의 실시간 영상, DRM 라이선스 요청을 원본 플러그인(127.0.0.1)에게 몰래 토스하고 결과를 돌려줍니다.
    """
    try:
        local_port = req.environ.get('SERVER_PORT', '9999')
        # 서버 내부로 향하는 다이렉트 주소 생성
        url = f"http://127.0.0.1:{local_port}{target_path}"
        if req.query_string:
            url += f"?{req.query_string.decode('utf-8')}"
            
        # 전송 길이를 꼬이게 만드는 불필요한 헤더는 제외하고 모두 복사
        headers = {k: v for k, v in req.headers.items() if k.lower() not in ['host', 'content-length']}
        
        # 원본 플러그인(alive 등)에 요청 중계
        res = requests.request(
            method=req.method,
            url=url,
            headers=headers,
            data=req.get_data(),
            cookies=req.cookies,
            allow_redirects=False,
            stream=True,  # 🌟 용량이 큰 영상 스트림이나 청크를 위해 필수!
            timeout=30
        )
        
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp_headers = [(k, v) for k, v in res.raw.headers.items() if k.lower() not in excluded_headers]
        
        # 스트리밍 발전기 함수 (영상이 끊기지 않도록 잘게 쪼개서 실시간 전송)
        def generate():
            for chunk in res.iter_content(chunk_size=1048576): # 1MB 단위
                if chunk:
                    yield chunk
                    
        return Response(stream_with_context(generate()), status=res.status_code, headers=resp_headers, content_type=res.headers.get('Content-Type'))
        
    except Exception as e:
        P.logger.error(f"[addrhide] Universal Route Error: {e}")
        P.logger.error(traceback.format_exc())
        return Response("재생 중계 오류", status=500)
