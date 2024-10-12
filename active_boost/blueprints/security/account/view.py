from argon2 import PasswordHasher
from sanic import Blueprint
from sanic_security.authentication import (
    requires_authentication,
    validate_password,
)
from sanic_security.utils import json

from active_boost.blueprints.security.account.models import Profile

account_bp = Blueprint("account")
password_hasher = PasswordHasher()


@account_bp.get("account/you")
@requires_authentication
async def on_account_get(request):
    profile = await Profile.get_from_account(request.ctx.authentication_session.bearer)
    return json(
        "Account retrieved.",
        {
            "account": request.ctx.authentication_session.bearer.json,
            "profile": profile.json,
        },
    )


@account_bp.delete("account/you")
@requires_authentication
async def on_my_account_delete(request):
    account = request.ctx.authentication_session.bearer
    account.deleted = True
    await account.save(update_fields=["deleted"])
    return json("Account deleted.", account.json)


@account_bp.put("account/you")
@requires_authentication
async def on_my_account_update(request):
    account = request.ctx.authentication_session.bearer
    account.username = request.form.get("username")
    account.email = request.form.get("email")
    if request.form.get("password"):
        account.password = password_hasher.hash(
            validate_password(request.form.get("password"))
        )
    await account.save(update_fields=["username", "email", "password"])
    return json("Account updated.", account.json)
