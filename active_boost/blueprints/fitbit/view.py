from sanic import Blueprint

from active_boost.common.models import BearerAuth
from active_boost.common.util import json, http_client

fitbit_bp = Blueprint("fitbit", url_prefix="fitbit")


# https://dev.fitbit.com/build/reference/web-api/


@fitbit_bp.get("goals")
async def on_get_activity_goals(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/activities/goals/{request.args.get("period")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Activity goals retrieved.", data.json())


@fitbit_bp.get("log")
async def on_get_activity_log(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/activities/list.json?"
        f"afterDate={request.args.get("after")}&sort=asc&limit=100&offset=0",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Activity log retrieved.", data.json())


@fitbit_bp.get("summary")
async def on_get_day_summary(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/activities/date/{request.args.get("date")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Day activity summary retrieved.", data.json())


@fitbit_bp.get("active-minutes")
async def on_get_active_minutes(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/activities/active-zone-minutes/date/"
        f"{request.args.get("start")}/{request.args.get("end")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Active minutes retrieved.", data.json())


@fitbit_bp.get("heartrate")
async def on_get_heartrate(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/activities/heart/date/{request.args.get("start")}/{request.args.get("end")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Heartrate series retrieved.", data.json())


@fitbit_bp.get("frequent")
async def on_get_frequent_activities(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/activities/frequent.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Frequent activities retrieved.", data.json())


@fitbit_bp.get("recent")
async def on_get_recent_activities(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/activities/recent.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Recent activities retrieved.", data.json())
