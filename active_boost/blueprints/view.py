from sanic import Blueprint

api_models = [
    "gpt_orchestrator.blueprints.chat.models",
    "gpt_orchestrator.blueprints.document.models",
    "gpt_orchestrator.blueprints.system.models",
    "gpt_orchestrator.blueprints.index.models",
    "sanic_security.models",
]

api = Blueprint.group(
    chat_bp,
    security_bp,
    account_bp,
    roles_bp,
    document_bp,
    system_bp,
    index_bp,
    version=1,
    version_prefix="/api/v",
)
