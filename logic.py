import traceback
from flask import Response, render_template
from .setup import *
from . import logic

class ModuleMain(PluginModuleBase):
    def __init__(self, P):
        super(ModuleMain, self).__init__(P, name="main", first_menu="setting")
        self.db_default = {
            f"{self.name}_db_version": "1",
            "id_mapping": "my_id : 기본_API키를_여기에_입력하세요",
        }

    def plugin_load(self):
        P.logger.info("AddrHide Plugin Loaded")

    def process_menu(self, sub, req):
        try:
            arg = P.ModelSetting.to_dict()
            if arg is None:
                arg = {}
            for key, value in self.db_default.items():
                if key not in arg:
                    arg[key] = value
            
            base_url = req.url_root.rstrip('/')
            arg['base_api_url'] = f"{base_url}/{P.package_name}/normal/"

            return render_template(f"{P.package_name}_{self.name}_{sub}.html", arg=arg)
            
        except Exception as e:
            P.logger.error(traceback.format_exc())
            return f"<h1>에러</h1><pre>{traceback.format_exc()}</pre>"

    def process_normal(self, sub, req):
        try:
            # 🌟 [핵심] 영상 재생이나 DRM 라이선스 등 실시간 요청이 들어오면 우회 라우터로 토스!
            if sub.startswith("route/"):
                # "route/alive/proxy/license" 같은 경로를 "/alive/proxy/license"로 변환
                target_path = sub.replace("route", "", 1)
                return logic.universal_route(target_path, req)
                
            # 기본적으로는 M3U 목록을 뽑아주는 로직 실행
            return logic.proxy_m3u(sub, req)
            
        except Exception as e:
            P.logger.error(traceback.format_exc())
            return Response(str(e), status=500, mimetype="text/plain")
