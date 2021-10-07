'''

    主視圖程式

    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/07
    update by : jay

'''

from flask import render_template, session

# ----- 自訂函式 -----
from . import main


@main.route('/')
def index():
    return render_template('main/index.html')
