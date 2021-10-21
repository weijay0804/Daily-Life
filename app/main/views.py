'''

    主視圖程式

    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/21
    update by : jay

'''

from flask import render_template, session, request, redirect, url_for
from flask.helpers import flash
from flask_login import login_required, current_user
from datetime import datetime

# ----- 自訂函式 -----
from . import main
from ..model import User
from .. import db


@main.route('/')
def index():
    return render_template('main/index.html')

@main.route('/user/<username>')
def user(username : str):
    ''' 使用者個人資訊頁面 '''

    now = datetime.utcnow()

    user = User.query.filter(User.username == username).first()
    return render_template('main/user.html', user = user, now = now)

@main.route('/edit-profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
    ''' 編輯使用者個人資訊頁面 '''

    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.location = request.form.get('location')
        current_user.about_me = request.form.get('about_me')
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('個人檔案已經更新')
        return redirect(url_for('main.user', username = current_user.username))

    form_datas = {
    'form_name' : current_user.name if current_user.name else '',
    'form_location' : current_user.location if current_user.location else '',
    'form_about_me' : current_user.about_me if current_user.about_me else '',
    }

    return render_template('main/edit_profile.html', **form_datas)

    