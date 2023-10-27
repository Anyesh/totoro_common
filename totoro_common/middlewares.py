import os
from functools import wraps

import jwt
from flask import current_app, request

from .exceptions import ApiException, NoDataProvidedApiException, OperationalException


def setup_prefix_middleware(app, prefix):
    if not app.config["TESTING"]:
        app.wsgi_app = PrefixMiddleware(app, prefix=prefix)

    return app


class PrefixMiddleware(object):
    ROUTE_NOT_FOUND_MESSAGE = "This url does not belong to the app."

    def __init__(self, app, prefix=""):
        self.app = app
        self.wsgi_app = app.wsgi_app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ["PATH_INFO"].startswith(self.prefix):
            environ["PATH_INFO"] = environ["PATH_INFO"][len(self.prefix) :]
            environ["SCRIPT_NAME"] = self.prefix
            return self.wsgi_app(environ, start_response)
        else:
            start_response("404", [("Content-Type", "text/plain")])
            return [self.ROUTE_NOT_FOUND_MESSAGE.encode()]


def post_data_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        json_data = request.get_json()
        if json_data is None or json_data == {}:
            raise NoDataProvidedApiException()
        else:
            return f(json_data, *args, **kwargs)

    return wrapped


def auth_requred(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        cookie_name = current_app.config.get("SESSION_COOKIE_NAME") or os.getenv(
            "SESSION_COOKIE_NAME"
        )
        if not cookie_name:
            raise OperationalException(
                "SESSION_COOKIE_NAME not set. Set that in .env file or in app config"
            )

        algorithm = current_app.config.get("COOKIE_ALGORITHM") or os.getenv(
            "COOKIE_ALGORITHM"
        )
        if not algorithm:
            raise OperationalException(
                "COOKIE_ALGORITHM not set. Set that in .env file or in app config"
            )

        secret_key = current_app.config.get("SECRET_KEY") or os.getenv("SECRET_KEY")
        if not secret_key:
            raise OperationalException(
                "SECRET_KEY not set. Set that in .env file or in app config"
            )

        token = request.cookies.get(cookie_name)
        if not token:
            raise ApiException("Unauthorized", 401)
        if not hasattr(current_app, "redis"):
            raise OperationalException("Redis not initialized")

        if not current_app.redis.get(token):
            raise ApiException("Unauthorized", 401)

        request.user = jwt.decode(token, secret_key, algorithms=[algorithm])
        return f(*args, **kwargs)

    return wrapped
