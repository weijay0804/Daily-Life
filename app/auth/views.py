'''

    使用者相關視圖

    created date : 2021/10/05
    created by : jay

    last update : 2021/10/07
    update by : jay

'''

from flask import render_template, request, redirect, url_for, session, flash

# ----- 自訂函式 -----
from . import auth
from .. import db
from ..model import User

@auth.route('/register', methods = ['GET', 'POST'])
def register():
    ''' 使用者註冊 '''
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if password1 != password2:
            flash('密碼不相同')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email = email).first():
            flash('email 已經被使用')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username = username).first():
            flash('使用者名稱 已經被使用')
            return redirect(url_for('auth.register'))

        user = User(email = email, username = username, password = password1)

        db.session.add(user)
        db.session.commit()

        flash('註冊成功')
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
