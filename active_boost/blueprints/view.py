from sanic import Blueprint

from active_boost.blueprints.security.view import security_bp
from active_boost.blueprints.social.view import social_bp

api_models = [
    "active_boost.blueprints.security.account.models",
    "active_boost.blueprints.social.models",
    "sanic_security.models",
]

api = Blueprint.group(
    security_bp,
    social_bp,
    version=1,
    version_prefix="/api/v",
)
