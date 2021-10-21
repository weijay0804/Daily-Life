'''

    主視圖藍圖初始化

    created date : 2021/10/05
    created by : jay

    update date : 2021/10/21
    update by : jay

'''

from flask import Blueprint

# ----- 自訂函式 -----
from ..model import Permission

main = Blueprint('main', __name__)

@main.app_context_processor
def inject_permission():
    ''' 在模板 context 中加入 Permission類別 '''
    return dict(Permission = Permission)

from . import views
