'''

    主視圖程式

    created date : 2021/10/05

    created by : jay

'''

from flask import render_template

# ----- 自訂函式 -----
from . import main

@main.route('/')
def index():
    return render_template('index.html')
