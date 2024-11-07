from sanic import Blueprint

from active_boost.blueprints.group.view import group_bp, challenge_bp
from active_boost.blueprints.security.view import security_bp

api_models = [
    "active_boost.blueprints.group.models",
    "active_boost.blueprints.security.models",
]
api = Blueprint.group(
    security_bp,
    group_bp,
    challenge_bp,
    version=1,
    version_prefix="/api/v",
)
