import concurrent.futures
import unittest

import jwt
from flask import Flask
from totoro.helpers.middlewares import auth_required


class TestAuthRequiredDecorator(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["SESSION_COOKIE_NAME"] = "session_cookie"
        self.app.config["COOKIE_ALGORITHM"] = "HS256"
        self.app.config["SECRET_KEY"] = "secret_key"
        self.fake_jwt_token = jwt.encode(
            {"user": 1, "user_role": "user"},
            self.app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    def test_auth_required_valid_token(self):
        @self.app.route("/protected")
        @auth_required
        def protected_route():
            return "Access Granted"

        self.app.redis = {self.fake_jwt_token: "1"}

        with self.app.test_client() as client:
            client.set_cookie("localhost", "session_cookie", self.fake_jwt_token)
            response = client.get("/protected")
            self.assertEqual(response.status_code, 200)

    def test_auth_required_invalid_token(self):
        @self.app.route("/protected")
        @auth_required
        def protected_route():
            return "Access Granted"

        self.app.redis = {self.fake_jwt_token: "1"}
        with self.app.test_client() as client:
            res = client.get("/protected")
            self.assertEqual(res.status_code, 500)

        with self.app.test_client() as client:
            client.set_cookie("localhost", "session_cookie", "invalid_token")
            res = client.get("/protected")
            self.assertEqual(res.status_code, 500)

    def test_auth_required_missing_configuration(self):
        del self.app.config["SESSION_COOKIE_NAME"]
        del self.app.config["COOKIE_ALGORITHM"]
        del self.app.config["SECRET_KEY"]

        @self.app.route("/protected")
        @auth_required
        def protected_route():
            return "Access Granted"

        with self.app.test_client() as client:
            with self.assertRaises(KeyError):
                client.get("/protected")

    def test_auth_required_redis_not_initialized(self):
        @self.app.route("/protected")
        @auth_required
        def protected_route():
            return "Access Granted"

        with self.app.test_client() as client:
            client.set_cookie("localhost", "session_cookie", self.fake_jwt_token)
            response = client.get("/protected")

            assert response.status_code == 500

    def test_auth_required_thread_safe(self):
        # Set up a shared resource (e.g., a counter)
        shared_counter = 0

        self.app.redis = {self.fake_jwt_token: "1"}

        @self.app.route("/protected")
        @auth_required
        def protected_route():
            nonlocal shared_counter
            # Simulate some shared resource modification
            shared_counter += 1
            return f"Access Granted - Counter: {shared_counter}"

        # Helper function to make a request
        def make_request():
            with self.app.test_client() as client:
                # Use set_cookie to set cookies
                client.set_cookie("localhost", "session_cookie", self.fake_jwt_token)
                response = client.get("/protected")
                return response.data.decode("utf-8")

        # Number of concurrent requests
        num_requests = 10

        # Use ThreadPoolExecutor to simulate concurrent requests
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_requests
        ) as executor:
            # Submit concurrent requests
            futures = [executor.submit(make_request) for _ in range(num_requests)]

            # Wait for all threads to complete
            concurrent.futures.wait(futures)

            # Collect and check results
            results = [future.result() for future in futures]
            for result in results:
                assert "Access Granted" in result

            # Check if shared resource (counter) has been modified correctly
            assert shared_counter == num_requests


if __name__ == "__main__":
    unittest.main()
