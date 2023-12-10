import os

import requests
from flask import current_app, g, request


def create_session(app=None):
    app = app or current_app
    cookie_name = app.config.get("SESSION_COOKIE_NAME") or os.getenv(
        "SESSION_COOKIE_NAME"
    )
    if not cookie_name:
        raise ValueError("No session cookie name found")

    cookies = request.cookies.get(cookie_name)
    if not cookies:
        raise ValueError("No authentication cookie found")

    auth_cookie = {cookie_name: cookies}

    if "session" not in g:
        # Create a session object
        session = requests.Session()

        # Attach the authentication cookie to the session
        session.cookies.update(auth_cookie)

        # Store the session in the Flask context
        g.session = session

    return g.session
