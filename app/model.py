'''

    資料庫模型
     
    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/16
    update by : jay

'''

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

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
    users = db.relationship('User', backref = 'role', lazy = 'dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs) # 繼承 db.Model 中的 __init__ 方法
        if self.permissions is None:
            self.permissions = 0

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


class User(db.Model, UserMixin):
    ''' 使用者資料庫模型 '''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    email = db.Column(db.String(128), unique = True, index = True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

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


    def __repr__(self) -> str:
        return '<User %r>' % self.username

@login_manager.user_loader
def load_user(user_id : str) -> User:
    ''' 取得使用者 '''
    return User.query.get(int(user_id))