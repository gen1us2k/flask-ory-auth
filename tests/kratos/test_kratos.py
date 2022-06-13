import responses
from flask import session

from flask_ory_auth.kratos.client import Authentication
from flask_ory_auth.kratos.middleware import AuthenticationMiddleware

auth = Authentication("http://127.0.0.1:4433")


def set_context_processor(app):
    @app.context_processor
    def set_email_session():
        auth.set_user_to_session(session)
        return {
            "user": session.get("email"),
        }


@responses.activate
def test_authentication_middleware(app, client):
    app.wsgi_app = AuthenticationMiddleware(app.wsgi_app, "http://127.0.0.1:4433", "http://127.0.0.1:4455")

    url = "http://127.0.0.1:4433/sessions/whoami"
    responses.add(responses.GET, url=url, status=200, json={"identity": {"traits": {"email": "someone@example.com"}}})
    response = client.get("/")

    assert response.status_code == 404


@responses.activate
def test_authentication_middleware_unauthenticated(app, client):
    app.wsgi_app = AuthenticationMiddleware(app.wsgi_app, "http://127.0.0.1:4433", "http://127.0.0.1:4455")

    url = "http://127.0.0.1:4433/sessions/whoami"
    responses.add(responses.GET, url=url, status=401, json={"error": "Error"})
    response = client.get("/")

    assert response.status_code == 302
    assert response.headers['location'] == 'http://127.0.0.1:4455'


@responses.activate
def test_auth_client(app, client):
    auth = Authentication("http://127.0.0.1:4433")

    url = "http://127.0.0.1:4433/sessions/whoami"
    responses.add(responses.GET, url=url, status=200, json={"identity": {"traits": {"email": "someone@example.com"}}})

    auth.set_user_to_session(session)

    assert session.get("email") == "someone@example.com"
