'''

    測試 roles 資料表模組

    created date : 2021/10/16
    created by : jay


'''


import unittest

# ----- 自訂函式 -----
from app.model import Role, Permission
from app import create_app, db

class RolesModelTestCase(unittest.TestCase):
    ''' Role 單元測試 '''

    def setUp(self) -> None:
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_permission(self) -> None:
        ''' 測試 add_permission 方法 '''

        r = Role(name = 'User')
        r.add_permission(Permission.FOLLOW)
        r.add_permission(Permission.WRITE)

        self.assertTrue(r.permissions == (Permission.FOLLOW + Permission.WRITE))

    def test_remove_permission(self) -> None:
        ''' 測試 remove_permission 方法 '''

        r = Role(name = 'User')
        r.add_permission(Permission.FOLLOW)
        r.add_permission(Permission.WRITE)
        r.remove_permission(Permission.WRITE)

        self.assertTrue(r.permissions == Permission.FOLLOW)
        self.assertFalse(r.permissions == (Permission.FOLLOW + Permission.WRITE))

    def test_reset_permission(self) -> None:
        ''' 測試 reset_permission 方法 '''

        r = Role(name = 'User')
        r.add_permission(Permission.FOLLOW)
        r.add_permission(Permission.WRITE)
        r.reset_permission()

        self.assertTrue(r.permissions == 0)

    def test_has_permission(self) -> None:
        ''' 測試 has_permission 方法 '''

        r = Role(name = 'User')

        r.add_permission(Permission.FOLLOW)
        r.add_permission(Permission.COMMENT)

        self.assertTrue(r.has_permission(Permission.FOLLOW))
        self.assertTrue(r.has_permission(Permission.COMMENT))
        self.assertFalse(r.has_permission(Permission.WRITE))
        self.assertFalse(r.has_permission(Permission.MODERATE))
        self.assertFalse(r.has_permission(Permission.ADMIN))
