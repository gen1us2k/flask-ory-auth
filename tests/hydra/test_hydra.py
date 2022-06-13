import os

import responses

from flask_ory_auth.hydra.middleware import IntrospectionMiddleware
from tests.fixtures import hydra_discovery


@responses.activate
def test_introspection_middleware_wo_headers(app, client):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.wsgi_app = IntrospectionMiddleware(
        app.wsgi_app,
        "offline openid",
        "http://127.0.0.1:4445",
        "http://127.0.0.1:4455",
    )

    responses.add(
        responses.GET, url="http://127.0.0.1:4444/.well-known/openid-configuration", status=200, json=hydra_discovery
    )
    resp = client.get('/')

    assert resp.status_code == 302
    assert resp.headers['location'] == 'http://127.0.0.1:4455'


@responses.activate
def test_introspection_middleware_w_headers(app, client):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.wsgi_app = IntrospectionMiddleware(
        app.wsgi_app,
        "offline openid",
        "http://127.0.0.1:4445",
        "http://127.0.0.1:4455",
    )

    responses.add(
        responses.GET, url="http://127.0.0.1:4444/.well-known/openid-configuration", status=200, json=hydra_discovery
    )
    responses.add(responses.POST, url="http://127.0.0.1:4445/oauth2/introspect", status=200, json={"active": True})
    resp = client.get('/', headers={"Authorization": "Bearer token"})

    assert resp.status_code == 404


@responses.activate
def test_introspection_middleware_w_query_params(app, client):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.wsgi_app = IntrospectionMiddleware(
        app.wsgi_app,
        "offline openid",
        "http://127.0.0.1:4445",
        "http://127.0.0.1:4455",
    )

    responses.add(
        responses.GET, url="http://127.0.0.1:4444/.well-known/openid-configuration", status=200, json=hydra_discovery
    )
    responses.add(responses.POST, url="http://127.0.0.1:4445/oauth2/introspect", status=200, json={"active": True})
    resp = client.get('/', query_string={"access_token": "token"})

    assert resp.status_code == 404


@responses.activate
def test_introspection_middleware_broken_auth(app, client):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.wsgi_app = IntrospectionMiddleware(
        app.wsgi_app,
        "offline openid",
        "http://127.0.0.1:4445",
        "http://127.0.0.1:4455",
    )

    responses.add(
        responses.GET, url="http://127.0.0.1:4444/.well-known/openid-configuration", status=200, json=hydra_discovery
    )
    responses.add(responses.POST, url="http://127.0.0.1:4445/oauth2/introspect", status=401, json={"active": True})
    resp = client.get('/', headers={"Authorization": "Bearer token"})

    assert resp.status_code == 302
    assert resp.headers['location'] == 'http://127.0.0.1:4455'
