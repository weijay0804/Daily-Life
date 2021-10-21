'''

    自訂裝飾器

    created date : 2021/10/20
    created by : jay


'''

from functools import wraps
from typing import Any
from flask import abort
from flask_login import current_user

# ----- 自訂函式 -----
from .model import Permission

def permission_required(permission : Permission) -> Any:
    ''' 檢查用戶是否有特定權限 '''
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)
