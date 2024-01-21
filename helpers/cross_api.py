import os

import requests
from flask import current_app, g, request

from .token import decode_token
from .exceptions import OperationalException


def create_session(app=None, cookie=None):
    app = app or current_app
    cookie_name = app.config.get("SESSION_COOKIE_NAME") or os.getenv(
        "SESSION_COOKIE_NAME"
    )
    if not cookie_name:
        raise ValueError("No session cookie name found")
    token = cookie or request.cookies.get(cookie_name)
    if not token:
        raise ValueError("No authentication cookie found")

    if cookie is not None:
        # Direct cookie was provided, decode it and set the user in the request context
        secret_key = app.config.get("SECRET_KEY") or os.getenv("SECRET_KEY")
        if not secret_key:
            raise OperationalException(
                "SECRET_KEY not set. Set that in .env file or in app config"
            )
        algorithm = app.config.get("COOKIE_ALGORITHM") or os.getenv("COOKIE_ALGORITHM")
        if not algorithm:
            raise OperationalException(
                "COOKIE_ALGORITHM not set. Set that in .env file or in app config"
            )
        user = decode_token(cookie, secret_key, algorithm)
        request.user = user
        g.user = user

    auth_cookie = {cookie_name: token}

    if "session" not in g:
        # Create a session object
        session = requests.Session()

        # Attach the authentication cookie to the session
        session.cookies.update(auth_cookie)

        # Store the session in the Flask context
        g.session = session

    return g.session
