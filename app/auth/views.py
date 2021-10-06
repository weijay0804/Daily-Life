'''

    使用者相關視圖

    created date : 2021/10/05
    created by : jay

'''

from flask import render_template, request, redirect, url_for, session

# ----- 自訂函式 -----
from . import auth
from .. import db
from ..model import User

@auth.route('/register', methods = ['GET', 'POST'])
def register():
    ''' 使用者註冊 '''
    if request.method == 'POST':
        print('POST')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html')

@auth.route('/login')
def login():
    ''' 使用者登入 '''
    pass

@auth.route('/logout')
def logout():
    ''' 使用者登出 '''
    pass
