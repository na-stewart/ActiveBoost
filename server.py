import traceback

from sanic import Sanic, json
from sanic_security.authentication import (
    create_initial_admin_account,
    attach_refresh_encoder,
)
from tortoise.contrib.sanic import register_tortoise

from active_boost.blueprints.view import api, api_models
from active_boost.common.util import config

app = Sanic("active_boost")
app.blueprint(api)


@app.exception(Exception)
async def exception_parser(request, e):
    traceback.print_exc()
    return json(
        {
            "data": e.__class__.__name__,
            "message": str(e),
        },
        e.status_code if hasattr(e, "status_code") else 500,
    )


# app.config.PROXIES_COUNT = 1 Uncomment if hosted in cloud or with proxies.
register_tortoise(
    app,
    db_url=config.DATABASE_URL,
    modules={"models": api_models},
    generate_schemas=config.GENERATE_SCHEMAS,
)
create_initial_admin_account(app)
attach_refresh_encoder(app)
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=1, debug=config.DEBUG)
