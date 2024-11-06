import datetime

from sanic import Blueprint

from active_boost.blueprints.challenge.models import Challenge
from active_boost.blueprints.group.models import Group
from active_boost.blueprints.security.common import require_permissions
from active_boost.common.exceptions import (
    ChallengeExpiredError,
    InvalidThresholdTypeError,
    ThresholdNotMetError,
)
from active_boost.common.util import json

challenge_bp = Blueprint("challenge", url_prefix="challenge")


@challenge_bp.get("you")
async def on_get_user_challenges(request):
    """Retrieves challenges associated with user."""
    challenges = await Challenge.get_all_from_participant(request.ctx.account)
    return json(
        "User challenges retrieved.", [challenge.json for challenge in challenges]
    )


@challenge_bp.get("participants")
async def on_get_challenge_participants(request):
    """Retrieves users who have joined the challenge and completed the challenge."""
    challenge = await Challenge.get(id=request.args.get("id"), deleted=False)
    participants = await challenge.participants.filter(deleted=False).all()
    finishers = await challenge.participants.filter(deleted=False).all()
    return json(
        "Challenge participants retrieved.",
        {
            "participants": [participant.json for participant in participants],
            "finishers": [finisher.json for finisher in finishers],
        },
    )


@challenge_bp.get("/")
async def on_get_challenges(request):
    """
    Retrieve all challenges associated with a group.
    """
    challenges = await Challenge.get_all_from_group(request)
    return json("Challenges retrieved.", [challenge.json for challenge in challenges])


@challenge_bp.post("/")
@require_permissions("challenge:create")
async def on_create_challenge(request):
    """Creates challenge associated with group if creator is in that group."""
    group = await Group.get_from_member(
        request, request.ctx.account, request.args.get("group")
    )
    challenge = await Challenge.create(
        title=request.form.get("title"),
        description=request.form.get("description"),
        reward=request.form.get("reward"),
        penalty=request.form.get("penalty"),
        threshold=request.form.get("threshold"),
        threshold_type=request.form.get("threshold-type"),
        expiration_date=datetime.datetime.strptime(
            request.form.get("expiration-date"), "%Y-%m-%d %H:%M:%S"
        ),
        challenger=request.ctx.account,
        group=group,
    )
    return json("Challenge created.", challenge.json)


@challenge_bp.put("/")
@require_permissions("challenge:update")
async def on_update_challenge(request):
    """Update challenge information if permitted."""
    challenge = await Challenge.get_from_group(request)
    challenge.title = request.form.get("title")
    challenge.description = request.form.get("description")
    challenge.reward = request.form.get("reward")
    challenge.penalty = request.form.get("penalty")
    challenge.threshold = request.form.get("threshold")
    challenge.threshold_type = request.form.get("threshold-type")
    challenge.expiration_date = datetime.datetime.strptime(
        request.form.get("expiration-date"), "%Y-%m-%d %H:%M:%S"
    )
    await challenge.save(
        update_fields=[
            "title",
            "description",
            "reward",
            "threshold",
            "expiration_date",
            "penalty",
            "threshold_type",
        ]
    )
    return json("Challenge updated.", challenge.json)


@challenge_bp.delete("/")
@require_permissions("challenge:delete")
async def on_delete_challenge(request):
    """Deletes challenge if permitted."""
    challenge = await Challenge.get_from_group(request)
    challenge.delete = True
    await challenge.save(update_fields="delete")
    return json("Challenge deleted.", challenge.json)


@challenge_bp.put("join")
async def on_join_challenge(request):
    """Join challenge and be added to its participants list."""
    challenge = await Challenge.get_from_group_and_member(request, request.ctx.account)
    await challenge.participants.add(request.ctx.account)
    return json("Challenge joined", challenge.json)


@challenge_bp.put("redeem")
async def on_challenge_redeem(request):
    """Adds user to finishers list if threshold attempt (e.g., "distance", "steps", "heartrate") exceeds challenge requirements."""
    challenge = await Challenge.get_from_participant(request, request.ctx.account)
    if challenge.has_expired():
        raise ChallengeExpiredError()
    elif challenge.threshold_type != request.args.get("threshold-type"):
        raise InvalidThresholdTypeError()
    elif request.args.get("threshold-attempt") > challenge.threshold:
        await challenge.finishers.add(request.ctx.account)
        return json("Challenge redeemed.", challenge.json)
    else:
        raise ThresholdNotMetError()
