import os
from urllib.parse import parse_qs
from urllib.parse import urlparse

import responses

from flask_ory_auth.hydra.middleware import IntrospectionMiddleware
from tests.fixtures import hydra_discovery


@responses.activate
def test_introspection_middleware_wo_headers(app, client):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.wsgi_app = IntrospectionMiddleware(
        app.wsgi_app,
        "http://127.0.0.1:4455",
        "offline openid",
        "http://127.0.0.1:4445",
        "http://127.0.0.1:4444/.well-known/openid-configuration",
        "example_id",
    )

    responses.add(
        responses.GET, url="http://127.0.0.1:4444/.well-known/openid-configuration", status=200, json=hydra_discovery
    )
    resp = client.get('/')

    u = urlparse(resp.headers['location'])
    qs = parse_qs(u.query)
    assert resp.status_code == 302
    assert resp.headers['location'].startswith('http://127.0.0.1:4444/oauth2/auth')

    assert qs['response_type'] == ['code']
    assert qs['client_id'] == ['example_id']
    assert qs['scope'] == ['offline openid']

    assert qs['state'] != ""
