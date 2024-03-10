import json
import re
from functools import wraps

from flask import current_app
import logging

from helpers.exceptions import TaskLockException

logger = logging.getlogger("TotoroLogger")



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


def use_redis_lock(key, locking_data=1, ttl_min=None, release=False):
    if ttl_min is None:
        ttl_min = 2

    redis = current_app.redis
    lock_key = f"lock:{key}"
    logger.info(f"[Lock] Locking key {lock_key}")

    if release:
        logger.info(f"[Lock] Releasing lock {lock_key}")
        redis.delete(lock_key)
        return

    if redis.get(lock_key):
        remaining_ttl = redis.ttl(lock_key)
        logger.info(f"[Lock] Locking key {lock_key} is already locked")

        raise TaskLockException(
            f"Task is currently locked. Please wait {remaining_ttl} seconds.",
        )
    logger.info(f"[Lock] Locking key {lock_key} with data {locking_data}")
    redis.setex(lock_key, 60 * ttl_min, locking_data)
