'''

    主視圖藍圖初始化

    created date : 2021/10/05

    created by : jay

'''

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
