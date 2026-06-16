from flask import Blueprint

# 'addrhide'라는 이름으로 Blueprint(라우팅 그룹) 생성
blueprint = Blueprint('addrhide', __name__, template_folder='templates')

# logic.py의 내용을 불러와 라우팅 적용
from . import logic
