from sanic import Blueprint
from sanic_security.authentication import login, logout, register
from sanic_security.utils import json

from active_boost.blueprints.security.account.models import Profile

security_bp = Blueprint("security")


@security_bp.post("/register")
async def on_register(request):
    account = await register(request, verified=True)
    await Profile.create(account=account)
    response = json("Registration successful! Verification required.", account.json)
    return response


@security_bp.post("/login")
async def on_login(request):
    authentication_session = await login(request)
    response = json("Login successful.", authentication_session.bearer.json)
    authentication_session.encode(response)
    return response


@security_bp.post("/logout")
async def on_logout(request):
    authentication_session = await logout(request)
    response = json("Logout successful.", authentication_session.bearer.json)
    return response
