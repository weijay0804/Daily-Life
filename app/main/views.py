'''

    主視圖程式

    created date : 2021/10/05
    created by : jay

'''

from flask import render_template, session

# ----- 自訂函式 -----
from . import main

@main.route('/')
def index():
    user = session.get('username')
    return render_template('main/index.html', user = user)
