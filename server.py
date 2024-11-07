import traceback

from sanic import Sanic, json
from tortoise.contrib.sanic import register_tortoise

from active_boost.blueprints.security.view import initialize_security
from active_boost.blueprints.view import api, api_models
from active_boost.common.util import config

app = Sanic("active_boost")
app.blueprint(api)

# app.static("/", "static", name="activb_static")
# app.static("/", "static/index.html", name="activb_index")


@app.exception(Exception)
async def exception_parser(request, e):
    traceback.print_exc()
    return json(
        {
            "data": e.__class__.__name__,
            "message": str(e),
        },
        e.status_code if hasattr(e, "status_code") else 400,
    )


register_tortoise(
    app,
    db_url=config.DATABASE_URL,
    modules={"models": api_models},
    generate_schemas=config.GENERATE_SCHEMAS,
)
initialize_security(app)
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, workers=1, debug=config.DEBUG)
