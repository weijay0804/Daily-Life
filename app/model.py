'''

    資料庫模型
     
    created date : 2021/10/05
    created by : jay

'''

# ----- 自訂函式 -----
from app import db


class User(db.Model):
    ''' 使用者資料庫模型 '''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)


    def __repr__(self) -> str:
        return '<User %r>' % self.username