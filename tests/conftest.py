import logging

import pytest
from flask import Flask


@pytest.fixture(scope="module")
def app():
    """Create application for the tests."""
    _app = Flask(__name__)
    _app.testing = True
    _app.config['SECRET_KEY'] = 'something_insecure'

    _app.logger.setLevel(logging.CRITICAL)
    ctx = _app.test_request_context()
    ctx.push()
    yield _app
    ctx.pop()


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()
