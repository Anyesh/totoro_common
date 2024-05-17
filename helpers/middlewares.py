import inspect
import os
from functools import wraps

from flask import current_app, g, request

from .constants import ROLE_SCORE, RoleEnum
from .exceptions import ApiException, NoDataProvidedApiException, OperationalException
from .token import decode_token


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


def parse_request_with(schema=None):
    if schema and inspect.isclass(schema):
        schema = schema()

    def parser(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            json_data = request.get_json()
            if json_data is None or json_data == {}:
                raise NoDataProvidedApiException()
            else:
                json_data = schema.load(json_data) if schema else json_data
            return f(json_data, *args, **kwargs)

        return wrapped

    return parser


def auth_required(f, app=None):
    app = app or current_app

    @wraps(f)
    def wrapped(*args, **kwargs):
        cookie_name = app.config.get("SESSION_COOKIE_NAME") or os.getenv(
            "SESSION_COOKIE_NAME"
        )
        if not cookie_name:
            raise OperationalException(
                "SESSION_COOKIE_NAME not set. Set that in .env file or in app config"
            )

        algorithm = app.config.get("COOKIE_ALGORITHM") or os.getenv("COOKIE_ALGORITHM")
        if not algorithm:
            raise OperationalException(
                "COOKIE_ALGORITHM not set. Set that in .env file or in app config"
            )

        secret_key = app.config.get("SECRET_KEY") or os.getenv("SECRET_KEY")
        if not secret_key:
            raise OperationalException(
                "SECRET_KEY not set. Set that in .env file or in app config"
            )

        token = request.cookies.get(cookie_name)
        if not token:
            raise ApiException("Unauthorized: Invalid token", 401)
        if not hasattr(app, "redis"):
            raise OperationalException("Redis not initialized")

        if not app.redis.get(token):
            raise ApiException("Unauthorized: Invalid redis token", 401)

        user = decode_token(token, secret_key, algorithm)
        if not user.get("user_role") or user.get("user_role") == RoleEnum.UNVERIFIED:
            raise ApiException("Forbidden: Unverified user", 403)

        request.user = user
        # request.user will be deprecated soon

        g.user = user
        return f(*args, **kwargs)

    return wrapped


def subscription_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        user = g.user or request.user
        if not user:
            raise ApiException("Unauthorized: User not initialized yet", 400)

        if ROLE_SCORE.get(user.get("user_role")) < ROLE_SCORE.get(RoleEnum.FAMILY):
            raise ApiException("Forbidden: Unauthorized user", 403)

        return f(*args, **kwargs)

    return wrapped


def role_required(f, required_role=RoleEnum.ADMIN):
    @wraps(f)
    def wrapped(*args, **kwargs):
        user = g.user or request.user
        if not user:
            raise ApiException("Unauthorized: User not initialized yet", 400)

        if user.get("user_role") != required_role:
            raise ApiException("Forbidden: Unauthorized user", 403)

        return f(*args, **kwargs)

    return wrapped


def is_internal(secret):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.headers.get("internal-header") != secret:
                raise ApiException("Forbidden: Not allowed", 403)
            return func(*args, **kwargs)

        return wrapper

    return decorator
