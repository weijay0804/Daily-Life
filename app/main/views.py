'''

    主視圖程式

    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/26
    update by : jay

'''

from flask import render_template, session, request, redirect, url_for, abort, current_app, make_response
from flask.helpers import flash
from flask_login import login_required, current_user
from datetime import datetime

# ----- 自訂函式 -----
from . import main
from ..model import User, Role, Post, Permission, Comment
from .. import db
from ..decorators import admin_required, permission_required

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

    show_posts = 'all'
    if current_user.is_authenticated:
        show_posts = request.cookies.get('show_posts', 'all')
    
    if show_posts == 'following':
        query = current_user.following_posts.filter(Post.is_private == False)
    elif show_posts == 'all':
        query = Post.query.filter_by(is_private = False)
    elif show_posts == 'private':
        query = current_user.posts.filter_by(is_private = True)

    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page = current_app.config['POSTS_PER_PAGE'], error_out = False)
    posts = pagination.items
    

    return render_template('main/index.html', posts = posts, pagination = pagination, show_posts = show_posts)

@main.route('/all')
@login_required
def show_all_posts():
    ''' 顯示所有文章 '''

    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_posts', 'all', max_age=30 * 24 * 60 * 60)    # 30 days
    return resp

@main.route('/following_posts')
@login_required
def following_posts():
    ''' 顯示所有追蹤的文章 '''

    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_posts', 'following', max_age=30 * 24 * 60 * 60)
    return resp

@main.route('/private')
@login_required
def private_posts():
    ''' 顯示所有私人文章 '''

    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_posts', 'private', max_age= 30 * 24 * 60 * 60)

    return resp

@main.route('/user/<username>')
def user(username : str):
    ''' 使用者個人資訊頁面 '''

    now = datetime.utcnow()

    user = User.query.filter(User.username == username).first()
    if user is None:
        abort(404)
    
    if user == current_user:
        posts = user.posts.order_by(Post.timestamp.desc()).all()
    else:
        posts = user.posts.filter_by(is_private = False).order_by(Post.timestamp.desc()).all()
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


@main.route('/post/<int:id>', methods = ['GET', 'POST'])
def post(id):
    ''' 特定文章頁面 '''

    post = Post.query.get_or_404(id)

    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('請先登入')
            return redirect(url_for('auth.login'))
        comment_data = request.form.get('comment')
        comment = Comment(body = comment_data, post = post, author = current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash('留言已送出')
        return redirect(url_for('main.post', id = post.id))

    page = request.args.get('page', 1, type=int)
    
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page, per_page = 5, error_out = False)

    comments = pagination.items

    return render_template('main/post.html', posts = [post], comments = comments, pagination = pagination)


@main.route('/edit/<int:id>', methods = ['GET', 'POST'])
@login_required
def edit(id):
    ''' 修改文章頁面 '''

    post = Post.query.get_or_404(id)

    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)

    if request.method == 'POST':
        post_data = request.form.get('post')
        is_private = request.form.get('is_private')
        post.body = post_data
        if is_private == 'on':
            post.is_private = True
        else:
            post.is_private = False

        db.session.commit()

        flash('文章修改完成')
        return redirect(url_for('main.post', id =  post.id))

    return render_template('main/edit_post.html', post = post)

@main.route('/delete/<int:id>', methods = ['POST'])
@login_required
def delete(id):
    ''' 刪除貼文視圖 '''

    post = Post.query.get_or_404(id)

    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)

    if request.method == 'POST':
        db.session.delete(post)
        db.session.commit()

        flash('刪除成功')
    
    return redirect(url_for('main.index'))

    


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    ''' 使用者追隨視圖 '''

    user = User.query.filter_by(username = username).first()

    if not user:
        flash('無效的使用者')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('你已經關注該使用者')
        return redirect(url_for('main.user', username = username))
    
    current_user.follow(user)
    db.session.commit()
    flash(f'開始關注 {username} ')

    return redirect(url_for('main.user', username = username))


@main.route('/unfollow/<username>')
@login_required
def unfollow(username):
    ''' 解除關注視圖 '''

    user = User.query.filter_by(username = username).first()

    if not user:
        flash('無效的使用者')
        return redirect(url_for('main.index'))
    
    if not current_user.is_following(user):
        flash('錯誤')
        return redirect(url_for('main.user', username = username))

    current_user.unfollow(user)

    flash(f'你不再關注 {username} 了')
    return redirect(url_for('main.user', username = username))


@main.route('/following/<username>')
def following(username):
    ''' 顯示使用者關注的人 '''

    user = User.query.filter_by(username = username).first()

    if not user:
        flash('無效的使用者')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    pagination = user.following.paginate(page, per_page = 10, error_out = False)

    follows = [{'user' : item.following, 'timestamp' : item.timestamp} for item in pagination.items]

    return render_template('main/follow.html', user = user, title = f"{ user.username } 關注的人", endpoint = 'main.following', pagination = pagination, follows = follows)

@main.route('/followers/<username>')
def followers(username):
    ''' 顯示關注使用者的人 '''

    user = User.query.filter_by(username = username).first()

    if not user:
        flash('無效的使用者')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page = 10, error_out = False)

    follows = [{'user' : item.follower, 'timestamp' : item.timestamp} for item in pagination.items]

    return render_template('main/follow.html', user = user, title = f"關注 { user.username } 的人", endpoint = 'main.followers', pagination = pagination, follows = follows)


@main.route('/modrate')
@login_required
@permission_required(Permission.MODERATE)
def modrate():
    ''' 管理留言 '''

    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.join(Post, Post.id == Comment.post_id).filter(Post.is_private == False).order_by(Comment.timestamp.desc()).paginate(page, per_page = 10, error_out = False)
    comments = pagination.items
    return render_template('main/modrate.html', pagination = pagination, comments = comments)

@main.route('/modrate/disabled/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def disabled(id):
    ''' 禁止留言 '''

    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.commit()
    flash('留言已被禁止')
    return redirect(url_for('main.modrate', page = request.args.get('page', 1, type=int)))


@main.route('/modrate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def enable(id):
    ''' 解除禁止留言 '''

    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.commit()
    flash('已解除禁止')
    return redirect(url_for('main.modrate', page = request.args.get('page', 1, type=int)))


@main.route('/search', methods = ['POST'])
def search():
    ''' 搜尋功能視圖 '''

    if request.method == 'POST':
        search_date = request.form.get('search')
        if not search_date:
            return redirect(url_for('main.index'))
        
        users = User.query.filter(User.username.like(f'%{search_date.lower()}%')).order_by(User.username).all()

        return render_template('main/search.html', users = users)

    
@main.route('/test')
def test():
    a = [1,2,3,4]

    return f'<h1>This is {a[56]}</h1>'