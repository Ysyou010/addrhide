import os
import traceback
from flask import Response, render_template, request, jsonify
from framework import path_data  # ★ 로그 파일 경로를 찾기 위해 추가
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
            
            base_url = req.url_root.rstrip('/')
            arg['base_api_url'] = f"{base_url}/{P.package_name}/fx/"

            return render_template(f"{P.package_name}_{self.name}_{sub}.html", arg=arg)
            
        except Exception as e:
            P.logger.error(traceback.format_exc())
            return f"<h1>에러</h1><pre>{traceback.format_exc()}</pre>"

    # ★ 추가: 화면에서 로그 데이터를 요청할 때 파일을 읽어서 전달하는 함수
    def process_ajax(self, sub, req):
        try:
            if sub == "get_log":
                log_file = os.path.join(path_data, 'log', f"{P.package_name}.log")
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        return jsonify({"ret": "success", "data": f.read()})
                return jsonify({"ret": "error", "data": "로그 파일이 아직 생성되지 않았습니다."})
                
        except Exception as e:
            P.logger.error(traceback.format_exc())
            return jsonify({"ret": "error", "data": f"로그 읽기 에러: {str(e)}"})
