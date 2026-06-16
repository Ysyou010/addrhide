from plugin import *

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
            },
            {
                'uri': 'log', # ★ 요청하신 대로 'log'로 변경했습니다.
                'name': '로그',
            }
        ]
    },
    'setting_menu': None,
    'default_route': 'normal',
}

P = create_plugin_instance(setting)
