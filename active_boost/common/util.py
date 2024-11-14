import datetime
import random
import string

import httpx
from sanic import HTTPResponse

from sanic import json as sanic_json

from active_boost.common.models import Config

config = Config(
    {
        "DEBUG": True,
        "DATABASE_URL": "sqlite://db.sqlite3",
        "GENERATE_SCHEMAS": True,
        "APP_BUILD": "0.0.1",
        "SECRET": "ymYjBr6AFxv494nzklUj",
        "FITBIT_SECRET": "58e2c6749ba6cb49d4900debf47798b7",
        "FITBIT_CLIENT": "23PR33",
    }
)
http_client = httpx.AsyncClient()
activity_resource_options = [
    "calories",
    "distance",
    "elevation",
    "floors",
    "minutesVeryActive",
    "minutesFairlyActive",
    "steps",
]


def json(message: str, data, status_code: int = 200) -> HTTPResponse:
    """A preformatted Sanic json response."""
    return sanic_json(
        {"message": message, "code": status_code, "data": data}, status=status_code
    )


def str_to_bool(val: str) -> bool:
    """Takes string and tries to turn it into bool as human would do."""
    val = val.lower()
    if val in {
        "y",
        "yes",
        "yep",
        "yup",
        "t",
        "true",
        "on",
        "enable",
        "enabled",
        "1",
    }:
        return True
    elif val in {"n", "no", "f", "false", "off", "disable", "disabled", "0"}:
        return False
    elif val is None:
        return False
    else:
        raise ValueError(f"Invalid truth value {val}")


def get_expiration_date(days: int) -> datetime.datetime:
    """Retrieves the date after which something (such as a session) is no longer valid."""
    return (
        datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=days)
        if days > 0
        else None
    )


def get_code() -> str:
    """
    Generates random code.

    Returns:
        code
    """
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(6)
    )
