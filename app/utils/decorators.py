from functools import wraps
from flask_login import current_user
from flask import redirect, url_for
from flask_login import login_required

def role_required(role):
    def wrapper(func):
        @wraps(func)
        @login_required
        def decorated_view(*args, **kwargs):
            if current_user.role != role:
                return redirect(url_for("auth.login"))
            return func(*args, **kwargs)
        return decorated_view
    return wrapper