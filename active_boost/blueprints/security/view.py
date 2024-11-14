import time

import jwt
from httpx_oauth.oauth2 import OAuth2
from sanic import Blueprint, redirect, Sanic
from tortoise.exceptions import IntegrityError

from active_boost.blueprints.security.models import Account
from active_boost.common.exceptions import AnonymousUserError, AuthorizationError
from active_boost.common.util import config, json

security_bp = Blueprint("security", url_prefix="security")
o_auth = OAuth2(
    config.FITBIT_CLIENT,
    config.FITBIT_SECRET,
    "https://www.fitbit.com/oauth2/authorize",
    "https://api.fitbit.com/oauth2/token",
    refresh_token_endpoint="https://api.fitbit.com/oauth2/token",
    token_endpoint_auth_method="client_secret_basic",
)


@security_bp.put("account")
async def on_update_account(request):
    request.ctx.account.username = request.form.get("username")
    request.ctx.account.bio = request.form.get("bio")
    request.ctx.account.icon_url = request.form.get("pfp_url")
    await request.ctx.account.save(update_fields=["username", "bio", "icon_url"])
    return json("Account updated.", request.ctx.account.json)


@security_bp.delete("account")
async def on_delete_account(request):
    request.ctx.account.deleted = True
    await request.ctx.account.save(update_fields=["deleted"])
    return json("Account deleted.", request.ctx.account.json)


@security_bp.route("login", methods=["GET", "POST"])
async def on_oauth_login(request):
    """Initialize OAuth login procedure or directly refresh access token."""
    if request.args.get("refresh-token"):
        request.ctx.token_info = await o_auth.refresh_token(
            request.args.get("refresh-token")
        )
        request.ctx.token_info["is_refresh"] = True
        response = json(
            "User authenticated and token stored, you may utilize all endpoints now.",
            request.ctx.token_info,
        )
    else:
        authorization_url = await o_auth.get_authorization_url(
            "https://activeboost.na-stewart.com/api/v1/security/callback",
            scope=[
                "activity",
                "heartrate",
                "nutrition",
                "oxygen_saturation",
                "respiratory_rate",
                "sleep",
                "temperature",
                "weight",
                "cardio_fitness",
            ],
        )
        response = redirect(authorization_url)
    return response


@security_bp.get("callback")
async def on_oauth_callback(request):
    """Retrieve OAuth access token via code provided by authentication server."""
    token_info = await o_auth.get_access_token(
        request.args.get("code"),
        "https://activeboost.na-stewart.com/api/v1/security/callback",
    )
    response = json(
        "User authenticated and token stored, you may utilize all endpoints now.",
        token_info,
    )
    response.cookies.add_cookie(
        "tkn_activb",
        jwt.encode(token_info, config.SECRET, algorithm="HS256"),
        httponly=True,
    )
    return response


@security_bp.route("logout", methods=["GET", "POST"])
async def on_logout(request):
    response = json("Logged out.", request.ctx.account.json)
    response.delete_cookie("tkn_activb")
    return response


def initialize_security(app: Sanic) -> None:
    @app.on_request
    async def token_acquisition_middleware(request):
        """Inject account and OAuth token information into request context."""
        if request.cookies.get("tkn_activb"):
            request.ctx.token_info = jwt.decode(
                request.cookies.get("tkn_activb"), config.SECRET, algorithms=["HS256"]
            )
            try:
                account = await Account.create(
                    user_id=request.ctx.token_info["user_id"],
                    username=request.ctx.token_info["user_id"],
                )
            except IntegrityError:
                account = await Account.get(user_id=request.ctx.token_info["user_id"])
            request.ctx.account = account
            if request.ctx.account.disabled or request.ctx.account.deleted:
                raise AuthorizationError("Account is disabled.")
            if time.time() > request.ctx.token_info["expires_at"]:
                request.ctx.token_info = await o_auth.refresh_token(
                    request.ctx.token_info["refresh_token"]
                )
                request.ctx.token_info["is_refresh"] = True
        elif "login" not in request.url and "callback" not in request.url:
            raise AnonymousUserError()

    @app.on_response
    async def refresh_encoder_middleware(request, response):
        """Encode newly refreshed access tokens."""
        if hasattr(request.ctx, "token_info") and request.ctx.token_info.get(
            "is_refresh"
        ):
            response.cookies.add_cookie(
                "tkn_activb",
                jwt.encode(request.ctx.token_info, config.SECRET, algorithm="HS256"),
                httponly=True,
            )
