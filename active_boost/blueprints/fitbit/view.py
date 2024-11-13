from sanic import Blueprint

from active_boost.common.models import BearerAuth
from active_boost.common.util import json, http_client

fitbit_bp = Blueprint("fitbit", url_prefix="fitbit")


# https://dev.fitbit.com/build/reference/web-api/


@fitbit_bp.get("activity")
async def on_get_activity_log(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/activities/list.json?"
        f"afterDate={request.args.get("after")}&sort=desc&limit=100&offset=0",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Activity log retrieved.", data.json())


@fitbit_bp.get("active-minutes")
async def on_get_active_minutes(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/activities/active-zone-minutes/date/"
        f"{request.args.get("start")}/{request.args.get("end")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Active minutes retrieved.", data.json())


@fitbit_bp.get("heart-rate")
async def on_get_heart_rate(request):
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


@fitbit_bp.get("sleep")
async def on_get_sleep(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/sleep/date/{request.args.get("start")}/{request.args.get("end")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Sleep log retrieved.", data.json())


@fitbit_bp.get("temperature")
async def on_get_temperature(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/skin/date/{request.args.get("start")}/{request.args.get("end")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Temperature log retrieved.", data.json())


@fitbit_bp.get("spo2")
async def on_get_spo2(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/spo2/date/{request.args.get("start")}/{request.args.get("end")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("SpO2 log retrieved.", data.json())


@fitbit_bp.get("fitness-score")
async def on_get_fitness_score(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/cardioscore/date/{request.args.get("start")}/{request.args.get("end")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Fitness score log retrieved.", data.json())


@fitbit_bp.get("heart-rate-variability")
async def on_get_heart_rate_variability(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/hrv/date/{request.args.get("start")}/{request.args.get("end")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Heart rate variability log retrieved.", data.json())


@fitbit_bp.get("breathing-rate")
async def on_get_breathing_rate(request):
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/br/date/{request.args.get("start")}/{request.args.get("end")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Breathing rate log retrieved.", data.json())


@fitbit_bp.get("body")
async def on_get_body(request):
    if request.args.get("type") not in ["bmi", "fat", "weight"]:
        raise ValueError("Log type must be bmi, fat, or weight.")
    data = await http_client.get(
        f"https://api.fitbit.com/1/user/{request.ctx.account.user_id}/body/{request.args.get("type")}/date/{request.args.get("start")}/{request.args.get("end")}.json",
        auth=BearerAuth(request.ctx.token_info["access_token"]),
    )
    return json("Body log retrieved.", data.json())
