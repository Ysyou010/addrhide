import traceback
from flask import Response, render_template, request
from plugin import F  # ★ 프레임워크 전역 객체(F) 가져오기
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
            
            # ★ F 객체를 통해 안전하게 DDNS를 가져옵니다.
            sys_ddns = F.SystemModelSetting.get('ddns')
            base_url = sys_ddns.rstrip('/') if sys_ddns else req.url_root.rstrip('/')
            
            arg['base_api_url'] = f"{base_url}/{P.package_name}/fx/"

            return render_template(f"{P.package_name}_{self.name}_{sub}.html", arg=arg)
            
        except Exception as e:
            P.logger.error(traceback.format_exc())
            return f"<h1>에러</h1><pre>{traceback.format_exc()}</pre>"
            
            # ★ F 객체를 통해 안전하게 DDNS를 가져옵니다.
            sys_ddns = F.SystemModelSetting.get('ddns')
            base_url = sys_ddns.rstrip('/') if sys_ddns else req.url_root.rstrip('/')
            
            arg['base_api_url'] = f"{base_url}/{P.package_name}/fx/"

            return render_template(f"{P.package_name}_{self.name}_{sub}.html", arg=arg)
            
        except Exception as e:
            P.logger.error(traceback.format_exc())
            return f"<h1>에러</h1><pre>{traceback.format_exc()}</pre>"
