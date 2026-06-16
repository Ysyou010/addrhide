from plugin import *

# FlaskFarm 프레임워크 표준 플러그인 설정 규격
setting = {
    'filepath' : __file__,
    'use_db': True,
    'use_default_setting': True,
    'home_module': None,
    'menu': {
        'uri': __package__,
        'name': '주소 숨김 프록시',
        'list': [
            {
                'uri': 'main/setting',
                'name': '설정',
            }
        ]
    },
    'setting_menu': None,
    'default_route': 'normal',
}

# 프레임워크에 플러그인 객체(P) 생성 및 등록
P = create_plugin_instance(setting)
