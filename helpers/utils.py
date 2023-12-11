import json
import re
from functools import wraps

from flask import current_app


def regex_password_validator(password):
    if not re.search(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&].{7,}$",
        password,
    ):
        raise ValueError(
            "Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number and one special character"
        )


def cached_method(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self_ = args[0]
        args_ = args[1:]
        kwargs_ = kwargs
        key = json.dumps((func.__name__, args_, kwargs_))
        cached = current_app.redis.get(key)
        if cached:
            return json.loads(cached)
        res = func(self_, *args_, **kwargs)
        current_app.redis.setx(key, json.dumps(res), 60 * 60 * 24)  # 1 day
        return res

    return wrapper
