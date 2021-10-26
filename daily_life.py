'''

    daily life 主程式

    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/06
    update by : jay

'''

from flask_migrate import Migrate

# ----- 自訂函式 -----
from app import create_app, db
from app.model import User, Role, Post

app = create_app('default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db = db, User = User, Role = Role, Post = Post)

@app.cli.command()
def test():
    ''' 啟動單元測試 '''
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)