'''

    資料庫模型
     
    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/07
    update by : jay

'''

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# ----- 自訂函式 -----
from app import db
from . import login_manager


class User(db.Model, UserMixin):
    ''' 使用者資料庫模型 '''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    email = db.Column(db.String(128), unique = True, index = True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self) -> None:
        ''' 讓外不無法直接讀取密碼 '''
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