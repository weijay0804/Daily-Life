'''

    錯誤處理路由

'''

from flask import render_template


# ----- 自定函式 -----
from . import main

@main.app_errorhandler(404)
def page_not_found(e):
    ''' 404 頁面不存在 '''

    return render_template('errors/404.html')

@main.app_errorhandler(403)
def forbidden(e):
    ''' 權限不足 '''

    return render_template('errors/403.html')
    
@main.app_errorhandler(500)
def server_error(e):
    ''' 伺服器錯誤 '''

    return render_template('errors/500.html')