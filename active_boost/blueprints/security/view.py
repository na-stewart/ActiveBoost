import time

import jwt
from httpx_oauth.oauth2 import OAuth2
from sanic import Blueprint, redirect, text

from active_boost.blueprints.security.models import Account
from active_boost.common.exceptions import AnonymousError
from active_boost.common.util import config

security_bp = Blueprint("security", url_prefix="security")
client = OAuth2(
    config.FITBIT_CLIENT,
    config.FITBIT_SECRET,
    "https://www.fitbit.com/oauth2/authorize",
    "https://api.fitbit.com/oauth2/token",
    refresh_token_endpoint="https://api.fitbit.com/oauth2/token",
    token_endpoint_auth_method="client_secret_basic",
)


@security_bp.get("login")
async def on_oauth_login(request):
    authorization_url = await client.get_authorization_url(
        "http://127.0.0.1:8000/api/v1/security/callback",
        scope=[
            "activity",
            "heartrate",
            "nutrition",
            "oxygen_saturation",
            "respiratory_rate",
            "sleep",
            "temperature",
            "weight",
        ],
    )
    return redirect(authorization_url)


@security_bp.get("callback")
async def on_oauth_callback(request):
    token_info = await client.get_access_token(
        request.args.get("code"), "http://127.0.0.1:8000/api/v1/security/callback"
    )
    await Account.get_or_create(user_id=token_info["user_id"])
    response = redirect("/")
    response.cookies.add_cookie(
        "tkn_activb",
        jwt.encode(token_info, config.SECRET, algorithm="HS256"),
        httponly=True,
    )
    return response


@security_bp.on_request
async def token_acquisition_middleware(request):
    if request.cookies.get("tkn_activb"):
        client_token_info = jwt.decode(
            request.cookies.get("tkn_activb"), config.SECRET, algorithms=["HS256"]
        )
        request.ctx.account = await Account.get(user_id=client_token_info["user_id"])
        if int(time.time()) > client_token_info["expires_at"]:
            token_info = await client.refresh_token(client_token_info["refresh_token"])
            request.ctx.token_info = token_info
            request.ctx.token_info["is_refresh"] = True

        else:
            request.ctx.token_info = client_token_info
    else:
        raise AnonymousError()


@security_bp.on_response
async def refresh_encoder_middleware(request, response):
    if request.ctx.token_info.get("is_refresh"):
        response.cookies.add_cookie(
            "tkn_activb",
            jwt.encode(request.ctx.token_info, config.SECRET, algorithm="HS256"),
            httponly=True,
        )


@security_bp.get("logout")
async def on_logout(request):
    response = text("Logged out.")
    response.delete_cookie("tkn_activb")
    response.delete_cookie("session")
    return response
