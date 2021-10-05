'''

    使用者相關視圖藍圖初始化

    created date : 2021/10/05
    created by : jay

'''

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
