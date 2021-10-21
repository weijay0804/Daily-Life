'''

    主視圖程式

    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/21
    update by : jay

'''

from flask import render_template, session
from datetime import datetime

# ----- 自訂函式 -----
from . import main
from ..model import User


@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/user/<username>')
def user(username : str):
    ''' 使用者個人資訊頁面 '''

    now = datetime.utcnow()

    user = User.query.filter(User.username == username).first()
    return render_template('main/user.html', user = user, now = now)
