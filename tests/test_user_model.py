'''

    User模組相關功能單元測試

    created date : 2021/10/06
    created by : jay

'''

import unittest

# ----- 自訂函式 -----
from app import create_app, db
from app.model import User

class UserModelTestCase(unittest.TestCase):
    ''' User 模組單元測試'''
    
    def setUp(self) -> None:
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self) -> None:
        ''' 測試 password setter 函式 '''
        u = User(username = 'test', password = 'cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self) -> None:
        ''' 測試 外部無法直接讀取 password 值 '''
        u = User(username = 'test', password = 'cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self) -> None:
        ''' 測試 檢查密碼函式 '''
        u = User(username = 'test', password = 'cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_is_random(self) -> None:
        ''' 測試 雜湊函式的 salts 是否為隨機 '''
        u1 = User(username = 'test', password = 'cat')
        u2 = User(username = 'test2', password = 'cat')
        self.assertFalse(u1.password_hash == u2.password_hash)