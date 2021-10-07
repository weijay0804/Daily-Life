'''

    使用者相關視圖

    created date : 2021/10/05
    created by : jay

    last update : 2021/10/07
    update by : jay

'''

from flask import render_template, request, redirect, session, url_for, flash
from flask_login import login_user, logout_user, login_required

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
        return redirect(url_for('auth.login'))
    

    return render_template('auth/register.html')

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    ''' 使用者登入 '''

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')

        is_remember_me = False if remember_me == None else True # 判斷 (記得我) 是否勾選

        user = User.query.filter_by(email = email).first()
        
        if user is not None and user.verify_password(password):
            login_user(user, is_remember_me)
            next = request.args.get('next')

            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            
            flash('登入成功')
            return redirect(next)

        flash('錯誤的 email 或 密碼')

    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    ''' 使用者登出 '''

    logout_user()
    flash('你已經登出')
    return redirect(url_for('main.index'))
