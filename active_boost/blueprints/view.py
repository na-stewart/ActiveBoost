from sanic import Blueprint

api_models = [
    "active_boost.blueprints.econ.models"
    "active_boost.blueprints.social.models"
    "sanic_security.models",
]

api = Blueprint.group(
    version=1,
    version_prefix="/api/v",
)
