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
            # 🌟 추가된 부분: 라이선스 해독 요청이 오면 전용 프록시로 연결
            if sub == "license":
                return logic.license_proxy(req)
                
            return logic.proxy_m3u(sub, req)
        except Exception as e:
            P.logger.error(traceback.format_exc())
            return Response(str(e), status=500, mimetype="text/plain")
