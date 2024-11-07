import datetime

from sanic import Blueprint

from active_boost.blueprints.group.models import Group, Challenge
from active_boost.blueprints.security.common import require_permissions, assign_role
from active_boost.blueprints.security.models import Role, Account
from active_boost.common.exceptions import (
    ChallengeExpiredError,
    InvalidThresholdTypeError,
    ThresholdNotMetError,
)
from active_boost.common.util import json, str_to_bool

group_bp = Blueprint("group", url_prefix="group")
challenge_bp = Blueprint("challenge", url_prefix="group/challenge")


@group_bp.get("you")
async def on_get_user_groups(request):
    """Retrieves groups associated with user."""
    groups = await Group.get_all_from_member(request.ctx.account)
    return json("User groups retrieved.", [group.json for group in groups])


@group_bp.get("members")
async def on_get_group_members(request):
    """Retrieves members of a group and their point value in that group."""
    # Super not optimal wtf?
    group = await Group.get(id=request.args.get("id"), deleted=False)
    members = await group.members.filter(deleted=False).all()
    challenges = await Challenge.get_all_from_group(request, request.args.get("id"))
    response_array = []
    for member in members:
        group_balance = (
            0  # The total amount of points accrued from completed challenges per group.
        )
        for challenge in challenges:
            if await challenge.finishers.filter(
                id=member.id
            ).exists():  # Has member completed the challenge?
                group_balance += challenge.reward
            elif (
                await challenge.participants.filter(id=member.id).exists()
                and challenge.has_expired()
            ):
                group_balance -= challenge.reward / 4
        response_array.append(
            {
                "account": member.username,
                "balance": group_balance,
            }
        )

    return json("Group members retrieved.", response_array)


@group_bp.get("/")
async def on_get_all_public_groups(request):
    """Retrieves all groups not marked as private."""
    groups = await Group.filter(deleted=False, private=False).all()
    return json("Public groups retrieved.", [group.json for group in groups])


@group_bp.post("/")
async def on_create_group(request):
    """Creates a group and are assigned all permissions for that group to allow full access."""
    group = await Group.create(
        title=request.form.get("title"),
        description=request.form.get("description"),
        private=str_to_bool(request.form.get("private")),
        founder=request.ctx.account,
    )
    await group.members.add(request.ctx.account)
    await assign_role(
        "Manager",
        group.id,
        request.ctx.account,
        "*",
        "Has complete control over group operations.",
    )
    return json("Group created.", group.json)


@group_bp.put("/")
@require_permissions("update")
async def on_update_group(request):
    """Update group information if permitted."""
    group = await Group.get(id=request.args.get("id"), deleted=False)
    group.title = request.form.get("title")
    group.description = request.form.get("description")
    group.private = str_to_bool(request.form.get("private"))
    await group.save(update_fields=["title", "description", "private"])
    return json("Group updated.", group.json)


@group_bp.delete("/")
@require_permissions("delete")
async def on_delete_group(request):
    group = await Group.get(id=request.args.get("id"), deleted=False)
    group.deleted = True
    await group.save(update_fields=["deleted"])
    return json("Group deleted.", group.json)


@group_bp.put("join")
async def on_join_group(request):
    """Join group and be added to its members list."""
    group = await Group.get(id=request.args.get("id"), deleted=False)
    await group.members.add(request.ctx.account)
    return json("Group joined.", group.json)


@group_bp.get("roles")
@require_permissions("roles")
async def on_get_group_roles(request):
    """Retrieve group roles and view details if permitted."""
    roles = await Role.filter(
        permissions__startswith=f"group-{request.args.get("id")}", deleted=False
    ).all()
    return json("Group roles retrieved.", [role.json for role in roles])


@group_bp.put("roles/assign")
@require_permissions("roles")
async def on_permit_group_user(request):
    """User can create new role or add role to another account such as moderator, manager, etc."""
    account_being_permitted = await Account.get(
        id=request.args.get("account"), deleted=False
    )
    if request.args.get("role"):
        role = await Role.get(
            permissions__startswith=f"group-{request.args.get("id")}",
            id=request.args.get("role"),
            deleted=False,
        )
    else:
        role = await assign_role(
            request.form.get("name"),
            request.args.get("id"),
            request.ctx.account,
            request.form.get("permissions"),
            request.form.get("description"),
        )
    await account_being_permitted.roles.add(role)
    return json("Group participant assigned role.", role.json)


@group_bp.put("roles/prohibit")
@require_permissions("roles")
async def on_prohibit_group_user(request):
    """User can remove role from another account such as moderator, manager, etc."""
    account_being_prohibited = await Account.get(
        id=request.args.get("account"), deleted=False
    )
    role = await Role.get(
        permissons__startswith=f"group-{request.args.get("id")}",
        id=request.args.get("role"),
        deleted=False,
    )
    await account_being_prohibited.roles.remove(role)
    return json("Group participant role removed.", role.json)


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
            "threshold_type",
        ]
    )
    return json("Challenge updated.", challenge.json)


@challenge_bp.delete("/")
@require_permissions("challenge:delete")
async def on_delete_challenge(request):
    """Deletes challenge if permitted."""
    challenge = await Challenge.get_from_group(request)
    challenge.deleted = True
    await challenge.save(update_fields=["deleted"])
    return json("Challenge deleted.", challenge.json)


@challenge_bp.put("join")
async def on_join_challenge(request):
    """Join challenge and be added to its participants list."""
    challenge = await Challenge.get_from_group_and_member(request, request.ctx.account)
    await challenge.participants.add(request.ctx.account)
    return json("Challenge joined", challenge.json)


@challenge_bp.put("redeem")
async def on_challenge_redeem(request):
    # UPDATE TO UTILIZE FITBIT DATA.
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
