'''

    資料庫模型
     
    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/26
    update by : jay

'''

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from datetime import datetime
import hashlib

# ----- 自訂函式 -----
from app import db
from . import login_manager

class Permission:
    ''' 權限常數 '''

    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    ''' 使用者角色資料庫模型 '''

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)

    users = db.relationship('User', backref = 'role', lazy = 'dynamic') # 一對多的 ( 一 )

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs) # 繼承 db.Model 中的 __init__ 方法
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles() -> None:
        ''' 新增 使用者角色 到資料庫中 '''

        roles = {
            'User' : [Permission.FOLLOW, Permission.WRITE, Permission.COMMENT],
            'Moderator' : [Permission.FOLLOW, Permission.WRITE, Permission.COMMENT, Permission.MODERATE],
            'Administrator' : [Permission.FOLLOW, Permission.WRITE, Permission.COMMENT, Permission.MODERATE, Permission.ADMIN],
        }

        default_role = "User"

        for r in roles:
            role = Role.query.filter_by(name = r).first()
            if role is None:
                role = Role(name = r)   # 新增使用者角色到資料庫
            role.reset_permission()     # 初始化權限

            for perm in roles[r]:
                role.add_permission(perm)   # 增加權限到特定的使用者角色

            role.default = (role.name == default_role) 

            db.session.add(role)
        db.session.commit()

    def has_permission(self, perm : Permission) -> bool:
        ''' 檢查使用者有沒有特定權限 '''

        return (self.permissions & perm) == perm    # if user.permission = FOLLOW + WRITE = 3
                                                    # has_permisson(FOLLW) -> 3 & 1 = 1   1 = 1 true
                                                    # has_permission(ADMIN) -> 3 & 16 = 0  0 = 16 false

    def add_permission(self, perm : Permission) -> None:
        ''' 新增特定權限給使用者 '''

        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm : Permission) -> None:
        ''' 從使用者移除特定權限 '''

        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self) -> None:
        ''' 重新設定使用者權限 '''

        self.permissions = 0
        

    def __repr__(self) -> str:
        return '<Role %r>' % self.name

class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    is_private = db.Column(db.Boolean, default = False, nullable = False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    comments = db.relationship('Comment', backref = 'post', lazy = 'dynamic')



class Follow(db.Model):

    __tablename__ = 'follows'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key = True)  # 追隨的人
    follow_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key = True)  # 被追隨的人
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)


class Comment(db.Model):
    ''' 使用者評論資料庫模型 '''

    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


class User(db.Model, UserMixin):
    ''' 使用者資料庫模型 '''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    email = db.Column(db.String(128), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default = datetime.utcnow)  # 註冊日期
    last_seen = db.Column(db.DateTime(), default = datetime.utcnow)     # 上次登入日期
    avatar_hash = db.Column(db.String(32))

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # 一對多的 ( 多 )
    posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')   # 一對多的 ( 一 )
    comments = db.relationship('Comment', backref = 'author', lazy = 'dynamic')

    following = db.relationship(
        'Follow', foreign_keys = [Follow.user_id], 
        backref = db.backref('follower', lazy = 'joined'),
        lazy = 'dynamic', cascade = 'all, delete-orphan'
        )  # 使用者追隨中的人
    
    followers = db.relationship(
        'Follow', foreign_keys = [Follow.follow_id], 
        backref = db.backref('following', lazy = 'joined'),
        lazy = 'dynamic', cascade = 'all, delete-orphan'
        ) # 追隨使用者的人


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

        # 初始化使用者權限
        if self.role is None:
            if self.email == current_app.config['DAILY_LIFE_ADMIN']:
                self.role = Role.query.filter_by(name = 'Administrator').first()
            else:
                self.role = Role.query.filter_by(default = True).first()

        # 初始化使用者頭貼 hsah 值
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.gravatar_hash()

    @property
    def following_posts(self) -> Post:
        ''' 取得關注的使用者的文章 '''

        return Post.query.join(Follow, Follow.follow_id == Post.author_id).filter(Follow.user_id == self.id)

    @property
    def password(self) -> None:
        ''' 讓外部無法直接讀取密碼 '''
        raise AttributeError('Password is not a readablb attribute.')

    @password.setter
    def password(self, password : str) -> None:
        ''' 密碼雜湊化 '''
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password : str) -> bool:
        ''' 檢查密碼是否正確 '''
        return check_password_hash(self.password_hash, password)

    def can(self, perm : Permission) -> bool:
        ''' 檢查使用者是否有特定的權限 '''

        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self) -> bool:
        ''' 檢查使用者是否是管理員 '''

        return self.can(Permission.ADMIN)


    def ping(self) -> None:
        ''' 更新 使用者登入日期 '''
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar_hash(self) -> str:
        ''' 生成使用者默認頭貼 hash 值 '''

        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def gravatar(self, size : int = 100, default : str = 'identicon', rating : str = 'g') -> str:
        ''' 生成使用者頭像 URL '''

        url = 'https://gravatar.loli.net/avatar'
        
        return f'{url}/{self.avatar_hash}?s={size}&r={rating}&d={default}'   


    def is_following(self, user) -> bool:
        ''' 檢查使用者是否有追隨特定使用者 '''

        if user.id is None:
            return False

        return self.following.filter_by(follow_id = user.id).first() is not None  

    def  is_followed_by(self, user) -> bool:
        ''' 檢查使用者使否有被特定使用者追隨 '''  

        if user.id is None:
            return False
        
        return self.followers.filter_by(user_id = user.id).first() is not None


    def follow(self, user) -> None:
        ''' 追隨使用者 '''

        if not self.is_following(user):
            f = Follow(user_id = self.id, follow_id = user.id)
            db.session.add(f)
            db.session.commit()
    
    def unfollow(self, user) -> None:
        ''' 解除追隨 '''

        f = self.following.filter_by(follow_id = user.id).first()

        if f:
            db.session.delete(f)
            db.session.commit()

    def __repr__(self) -> str:
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    ''' 匿名用戶 '''

    def can(self, perm : Permission) -> bool:
        ''' 匿名用戶沒有權限 一律回傳 False '''

        return False

    def is_administrator(self) -> bool:
        ''' 一律回傳 False '''

        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id : str) -> User:
    ''' 取得使用者 '''
    return User.query.get(int(user_id))

