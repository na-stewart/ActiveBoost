from sanic import HTTPResponse


from sanic import json as sanic_json

from active_boost.common.models import Config

config = Config(
    {
        "DEBUG": True,
        "DATABASE_URL": "sqlite://:memory:",
        "GENERATE_SCHEMAS": True,
        "APP_BUILD": "0.0.1",
    }
)


def json(message: str, data, status_code: int = 200) -> HTTPResponse:
    """
    A preformatted Sanic json response.

    Args:
        message (int): Message describing data or relaying human-readable information.
        data (Any): Raw information to be used by user.
        status_code (int): HTTP response code.

    Returns:
        json
    """
    return sanic_json(
        {"message": message, "code": status_code, "data": data}, status=status_code
    )
