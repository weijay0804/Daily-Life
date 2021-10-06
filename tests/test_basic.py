'''

    app 基本單元測試

    created date : 2021/10/06
    created by : jay

'''

import unittest
from flask import current_app

# ----- 自訂函式 -----
from app import create_app, db

class BasicTestCase(unittest.TestCase):
    ''' 測試 app 基本屬性 '''

    def setUp(self) -> None:
        self.app = create_app('test')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exist(self) -> None:
        ''' 測試 app 是否存在 '''
        self.assertTrue(current_app is not None)

    def test_app_is_test(self) -> None:
        ''' 測試 app 是否在 test 環境 '''
        self.assertTrue(current_app.config['TESTING'])