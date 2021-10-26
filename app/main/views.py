'''

    主視圖程式

    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/26
    update by : jay

'''

from flask import render_template, session, request, redirect, url_for, abort
from flask.helpers import flash
from flask_login import login_required, current_user
from datetime import datetime

# ----- 自訂函式 -----
from . import main
from ..model import User, Role, Post, Permission
from .. import db
from ..decorators import admin_required

@main.route('/', methods = ['GET', 'POST'])
def index():

    if request.method == 'POST' and current_user.can(Permission.WRITE):
        post_data = request.form.get('post')
        is_private = request.form.get('is_private')
        if is_private == 'on':
            post = Post(body = post_data, author = current_user._get_current_object(), is_private = True)
        else:
            post = Post(body = post_data, author = current_user._get_current_object())
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('main.index'))
    
    posts = Post.query.order_by(Post.timestamp.desc()).all()

    return render_template('main/index.html', posts = posts)

@main.route('/user/<username>')
def user(username : str):
    ''' 使用者個人資訊頁面 '''

    now = datetime.utcnow()

    user = User.query.filter(User.username == username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('main/user.html', user = user, now = now, posts = posts)

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


@main.route('/edit-profile/<int:id>', methods = ['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    ''' 管理員編輯個人資料頁面 '''
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        form = request.form
        user.email = form.get('email')
        user.username = form.get('username')
        if int(form.get('role')):
            user.role = Role.query.get(int(form.get('role')))

        print(form.get('role'))
        print(bool(int(form.get('role'))))
        user.name = form.get('name')
        user.location = form.get('location')
        user.about_me = form.get('about_me')
        db.session.add(user)
        db.session.commit()
        flash('修改成功')
        return redirect(url_for('main.user', username = user.username))
    
    roles = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
    form_datas = {
        'form_email' : user.email,
        'form_username' : user.username,
        'form_name' : user.name if user.name else '',
        'form_location' : user.location if user.location else '',
        'form_about_me' : user.about_me if user.about_me else '',
        'roles' : roles
        }

    return render_template('main/edit_profile_admin.html', user = user, **form_datas)



