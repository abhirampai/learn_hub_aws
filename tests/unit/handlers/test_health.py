import json

from handlers import health


def test_health_handler_returns_application_version():
    response = health.lambda_handler({}, None)

    assert response["statusCode"] == 200
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {
        "status": "ok",
        "service": "Learn Hub",
        "version": "0.1.0",
    }
