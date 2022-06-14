import random
import string

import requests
from flask import Request
from flask import Response


class IntrospectionMiddleware:
    def __init__(self, app, scope=None, admin_url=None, login_url=None, callback_url=None):
        self.app = app
        self.login_url = login_url
        self.scope = scope
        self.admin_url = admin_url
        self.callback_url = callback_url

    def get_access_token(self, request):
        header = request.headers.get("Authorization")
        if not header:
            access_token = request.args.get("access_token", "")
            if access_token:
                return access_token

            access_token = request.form.get("access_token", "")
            if access_token:
                return access_token

            return None

        parts = header.split()
        return parts[1]

    def generate_state(self):
        alphabet = string.ascii_lowercase + string.digits + string.ascii_uppercase
        return ''.join(random.choice(alphabet) for i in range(32))

    def __call__(self, environ, start_response):
        request = Request(environ)
        token = self.get_access_token(request)

        if request.base_url in [self.login_url, self.callback_url]:
            return self.app(environ, start_response)

        if not token:
            response = Response()
            response.status_code = 302
            response.headers = [("Location", self.login_url)]
            return response(environ, start_response)

        resp = requests.post(
            f"{self.admin_url}/oauth2/introspect",
            data={
                "scope": self.scope,
                "token": token,
            },
        )
        if resp.status_code != 200:
            response = Response()
            response.status_code = 302
            response.headers = [("Location", self.login_url)]
            return response(environ, start_response)

        if resp.json().get('active', False):
            # FIXME: Handle it
            pass

        return self.app(environ, start_response)


class AccessControlMiddlware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)
