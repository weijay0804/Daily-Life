'''

    daily life 主程式

    created date : 2021/10/05
    created by : jay

    last update date : 2021/10/06
    update by : jay

'''

from flask_migrate import Migrate, upgrade
import os
import sys
import click

# ----- 自訂函式 -----
from app import create_app, db
from app.model import User, Role, Post

COV = None
# 啟動單元測試覆蓋率
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

app = create_app('default')
migrate = Migrate(app, db)




@app.shell_context_processor
def make_shell_context():
    return dict(db = db, User = User, Role = Role, Post = Post)


@app.cli.command()
def deploy():
    upgrade()
    Role.insert_roles()

    print('更新完成')


@app.cli.command()
@click.option('--coverage/--no-coverage', default = False, help = 'Run tests under coverage.')
def test(coverage):
    ''' 啟動單元測試 '''

    if coverage or not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))   # 重新啟動程式

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    # 覆蓋率
    if COV:
        COV.stop()
        COV.save()
        print('覆蓋率結果: ')
        COV.report()
        # 儲存覆蓋率資料
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print(f'HTML version: file://{covdir}//index.html')
        COV.erase()
