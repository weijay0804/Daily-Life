'''

    daily life 主程式

    created date : 2021/10/05

    created by : jay

'''

# ----- 自訂函式 -----
from app import create_app, db

app = create_app('default')

@app.shell_context_processor
def make_shell_context():
    return dict(db = db)