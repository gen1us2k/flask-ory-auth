import requests
from flask import Request
from flask import Response


class AuthenticationMiddleware:
    def __init__(self, app, api_url, ui_url):
        self.app = app
        self.api_url = api_url
        self.ui_url = ui_url

    def __call__(self, environ, start_response):
        request = Request(environ)
        resp = requests.get(
            f"{self.api_url}/sessions/whoami",
            cookies=request.cookies,
            headers={"Authorization": request.headers.get("Authorization", "")},
        )
        if resp.status_code != 200:
            response = Response()
            response.status_code = 302
            response.headers = [("Location", self.ui_url)]
            return response(environ, start_response)

        return self.app(environ, start_response)
