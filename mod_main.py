import traceback
from flask import Response, render_template
from .setup import *
from . import logic

class ModuleMain(PluginModuleBase):
    def __init__(self, P):
        super(ModuleMain, self).__init__(P, name="main", first_menu="setting")
        # DB 기본값 설정 (초기 설치 시 들어갈 데이터)
        self.db_default = {
            f"{self.name}_db_version": "1",
            "id_mapping": "my_id : 기본_API키를_여기에_입력하세요",
        }

    def plugin_load(self):
        P.logger.info("AddrHide Plugin Loaded")

    def process_menu(self, sub, req):
        # 웹 화면(UI) 진입 시 처리
        try:
            arg = P.ModelSetting.to_dict()
            if arg is None:
                arg = {}
            for key, value in self.db_default.items():
                if key not in arg:
                    arg[key] = value
            
            # 현재 서버의 기본 주소 생성 (예: http://www.ysyou0109.win:9999)
            base_url = req.url_root.rstrip('/')
            arg['base_api_url'] = f"{base_url}/{P.package_name}/api/"

            return render_template(f"{P.package_name}_{self.name}_{sub}.html", arg=arg)
        except Exception as e:
            P.logger.error(traceback.format_exc())
            return f"<h1>에러</h1><pre>{traceback.format_exc()}</pre>"

    def process_api(self, sub, req):
        # /addrhide/api/[id] 로 외부에서 접속 시 처리
        try:
            # sub 변수에 URL의 [id] 부분이 자동으로 들어옵니다.
            return logic.proxy_m3u(sub, req)
        except Exception as e:
            P.logger.error(traceback.format_exc())
            return Response(str(e), status=500, mimetype="text/plain")
