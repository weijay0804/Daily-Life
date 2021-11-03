"""

    產生偽造的使用者

"""

from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker

# ---- 自訂函式 ----
from . import db
from .model import User, Post


def users(count : int = 100) -> None:
    """ 產生特定數量的使用者 """

    fake = Faker()
    i = 0
    while i < count:
        u = User(username = fake.user_name(),
                email = fake.email(),
                password = 'password',
                name = fake.name(),
                location = fake.city(),
                about_me = fake.text(),
                member_since = fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()

def posts(count : int = 100) -> None:
    """ 產生特定數量的文章 """

    fake = Faker()
    user_count = User.query.count()

    for i in range(0, user_count):
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Post(body = fake.text(), timestamp = fake.past_date(), author = u)

        db.session.add(p)
    db.session.commit()



