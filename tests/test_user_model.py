'''

    User模組相關功能單元測試

    created date : 2021/10/06
    created by : jay

    update date : 2021/10/21
    update by : jay

'''

import unittest

# ----- 自訂函式 -----
from app import create_app, db
from app.model import Permission, User, Role, AnonymousUser

class UserModelTestCase(unittest.TestCase):
    ''' User 模組單元測試'''
    
    def setUp(self) -> None:
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

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

    def test_user_role(self) -> None:
        ''' 測試 使用者權限函式 '''
        u = User(username = 'test', email = 'test@gamil.com', password = 'test')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_AnonymousUser(self) -> None:
        ''' 測試 匿名用戶權限 '''
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_ping(self) -> None:
        ''' 測試 更新使用者登入時間函式 '''
        import time
        u = User(username = 'test', password = 'test', email = 'test@gamil.com')
        db.session.add(u)
        db.session.commit()
        last_seen_berfor = u.last_seen
        time.sleep(2)
        u.ping()
        self.assertTrue(u.last_seen > last_seen_berfor)

    def test_gravatar(self) -> None:
        ''' 測試 生成使用者默認頭貼 URL '''

        u = User(username = 'test', password = 'test', email = 'test@gmail.com')
        with self.app.test_request_context('/'):
            gravatar = u.gravatar(size = 256, default = 'wavatar', rating='pg')
        
        self.assertTrue(f'https://gravatar.loli.net/avatar/1aedb8d9dc4751e229a335e371db8058' in gravatar)
        self.assertTrue('s=256' in gravatar)
        self.assertTrue('r=pg' in gravatar)
        self.assertTrue('d=wavatar' in gravatar)

        

