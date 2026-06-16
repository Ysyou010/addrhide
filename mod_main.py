import traceback
from flask import Response, render_template, request
from framework import SystemModelSetting  # ★ 프레임워크 기본 설정 불러오기
from .setup import *
from . import logic

@P.blueprint.route('/fx/<path:sub>', methods=['GET', 'POST', 'OPTIONS', 'HEAD'])
def custom_fx_route(sub):
    try:
        if sub.startswith("route/"):
            target_path = "/" + sub.replace("route/", "", 1)
            return logic.universal_route(target_path, request)
        return logic.proxy_m3u(sub, request)
    except Exception as e:
        P.logger.error(traceback.format_exc())
        return Response(str(e), status=500, mimetype="text/plain")

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
            
            # ★ 핵심: 시스템 설정에서 DDNS를 가져오고, 없으면 기본 접속 주소를 사용합니다.
            sys_ddns = SystemModelSetting.get('ddns')
            base_url = sys_ddns.rstrip('/') if sys_ddns else req.url_root.rstrip('/')
            
            arg['base_api_url'] = f"{base_url}/{P.package_name}/fx/"

            return render_template(f"{P.package_name}_{self.name}_{sub}.html", arg=arg)
            
        except Exception as e:
            P.logger.error(traceback.format_exc())
            return f"<h1>에러</h1><pre>{traceback.format_exc()}</pre>"
