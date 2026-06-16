def universal_route(req):
    try:
        # 🌟 SJVA 라우팅 특성 대응: 잘려나간 경로 대신, 원본 요청 경로(req.path)에서 진짜 주소 추출
        if "/route" not in req.path:
            return Response("잘못된 라우트 경로", status=400)
            
        target_path = req.path.split("/route", 1)[1]
        
        local_port = req.environ.get('SERVER_PORT', '9999')
        url = f"http://127.0.0.1:{local_port}{target_path}"
        
        if req.query_string:
            url += f"?{req.query_string.decode('utf-8')}"
            
        # 요청 헤더: Host는 충돌 방지를 위해 제거하지만, Range(구간탐색) 관련 헤더는 살려야 합니다.
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
        
        # 🌟 [해결의 핵심] 로컬 MP4, MKV 파일의 탐색(Seek)을 위해 Content-Length와 Range 헤더를 절대로 지우면 안 됩니다!
        excluded_headers = ['content-encoding', 'transfer-encoding', 'connection', 'keep-alive', 'proxy-authenticate', 'te', 'trailers', 'upgrade']
        resp_headers = [(k, v) for k, v in res.raw.headers.items() if k.lower() not in excluded_headers]
        
        # 끊김 없이 1MB씩 안정적으로 실시간 전송 (헤더는 리스트 형태로 덮어씌움)
        return Response(
            stream_with_context(res.iter_content(chunk_size=1048576)), 
            status=res.status_code, 
            headers=resp_headers
        )
        
    except Exception as e:
        P.logger.error(f"[addrhide] Universal Route Error: {e}")
        P.logger.error(traceback.format_exc())
        return Response("재생 중계 오류", status=500)
