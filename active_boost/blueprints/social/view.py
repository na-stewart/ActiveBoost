import datetime

from sanic import Blueprint
from sanic_security.authentication import requires_authentication
from sanic_security.authorization import (
    assign_role,
)
from sanic_security.models import Account, Role

from active_boost.blueprints.security.account.models import Profile
from active_boost.blueprints.social.models import Group, Challenge
from active_boost.common.exceptions import (
    ThresholdNotMetError,
    ChallengeExpiredError,
    InvalidThresholdTypeError,
)
from active_boost.common.util import json, str_to_bool

social_bp = Blueprint("social")


@social_bp.get("groups/you")
@requires_authentication
async def on_get_user_groups(request):
    """Retrieves groups associated with user."""
    groups = await Group.get_all_from_member(request.ctx.authentication_session.bearer)
    return json("User groups retrieved.", [group.json for group in groups])


@social_bp.get("groups/members")
@requires_authentication
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
                group_balance -= challenge.penalty
            print(challenge.has_expired())
        profile = await Profile.get_from_account(member)
        response_array.append(
            {
                "account": member.username,
                "profile": profile.json,
                "balance": group_balance,
            }
        )

    return json("Group members retrieved.", response_array)


@social_bp.get("groups")
async def on_get_all_public_groups(request):
    """Retrieves all groups not marked as private."""
    groups = await Group.filter(deleted=False, private=False).all()
    return json("Public groups retrieved.", [group.json for group in groups])


@social_bp.post("groups")
@requires_authentication
async def on_create_group(request):
    """Creates a group and are assigned all permissions for that group to allow full access."""
    group = await Group.create(
        title=request.form.get("title"),
        description=request.form.get("description"),
        private=str_to_bool(request.form.get("private")),
        founder=request.ctx.authentication_session.bearer,
    )
    await group.members.add(request.ctx.authentication_session.bearer)
    # Not ideal but reduces complexity by having only three available roles per group for now.
    await assign_role(
        f"{group.title} Manager",
        request.ctx.authentication_session.bearer,
        f"group-{group.id}:group",
        f"Has complete control over {group.title}.",
    )
    await assign_role(
        f"{group.title} Challenges Manager",
        request.ctx.authentication_session.bearer,
        f"group-{group.id}:challenges",
        f"Has complete control over {group.title} challenges.",
    )
    await assign_role(
        f"{group.title} Moderator",
        request.ctx.authentication_session.bearer,
        f"group-{group.id}:moderation",
        f"Has complete control over {group.title} participants.",
    )
    return json("Group created.", group.json)


@social_bp.put("groups")
async def on_update_group(request):
    """Update group information if permitted."""
    await Group.check_group_user_permissions(request, "group")
    group = await Group.get(id=request.args.get("id"), deleted=False)
    group.title = request.form.get("title")
    group.description = request.form.get("description")
    group.private = str_to_bool(request.form.get("private"))
    await group.save(update_fields=["title", "description", "private"])
    return json("Group updated.", group.json)


@social_bp.delete("groups")
async def on_delete_group(request):
    """Delete group if permitted."""
    await Group.check_group_user_permissions(request, "group")
    group = await Group.get(id=request.args.get("id"), deleted=False)
    group.deleted = True
    await group.save(update_fields=["disbanded"])
    return json("Group deleted.", group.json)


@social_bp.put("groups/join")
@requires_authentication
async def on_join_group(request):
    """Join group and be added to its members list."""
    group = await Group.get(id=request.args.get("id"), deleted=False)
    await group.members.add(request.ctx.authentication_session.bearer)
    return json("Group joined.", group.json)


@social_bp.get("groups/roles")
async def on_get_group_roles(request):
    """Retrieve group roles and view details if permitted."""
    await Group.check_group_user_permissions(request, "group")
    roles = await Role.filter(
        permissions__startswith=f"group-{request.args.get("id")}", deleted=False
    ).all()
    return json("Group roles retrieved.", [role.json for role in roles])


@social_bp.put("groups/roles/assign")
async def on_permit_group_user(request):
    """User can add role to another account such as moderator, manager, etc."""
    await Group.check_group_user_permissions(request, "group")
    account_being_permitted = await Account.get(
        id=request.args.get("account"), deleted=False
    )
    role = await Role.get(
        permissions__startswith=f"group-{request.args.get("id")}",
        id=request.args.get("role"),
        deleted=False,
    )
    await account_being_permitted.roles.add(role)
    return json("Group participant assigned role.", role.json)


@social_bp.put("groups/roles/prohibit")
async def on_prohibit_group_user(request):
    """User can remove role from another account such as moderator, manager, etc."""
    await Group.check_group_user_permissions(request, "group")
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


@social_bp.get("challenges/you")
@requires_authentication
async def on_get_user_challenges(request):
    """Retrieves challenges associated with user."""
    challenges = await Challenge.get_all_from_participant(
        request.ctx.authentication_session.bearer
    )
    return json(
        "User challenges retrieved.", [challenge.json for challenge in challenges]
    )


@social_bp.get("challenges/participants")
@requires_authentication
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


@social_bp.get("challenges")
@requires_authentication
async def on_get_challenges(request):
    """
    Retrieve all challenges associated with a group.
    """
    challenges = await Challenge.get_all_from_group(request)
    return json("Challenges retrieved.", [challenge.json for challenge in challenges])


@social_bp.post("challenges")
async def on_create_challenge(request):
    """Creates challenge associated with group if creator is in that group."""
    authentication_session = await Group.check_group_user_permissions(
        request, "challenges", request.args.get("group")
    )
    group = await Group.get_from_member(
        request, authentication_session.bearer, request.args.get("group")
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
        challenger=authentication_session.bearer,
        group=group,
    )
    return json("Challenge created.", challenge.json)


@social_bp.put("challenges")
async def on_update_challenge(request):
    """Update challenge information if permitted."""
    await Group.check_group_user_permissions(
        request, "challenges", request.args.get("group")
    )
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


@social_bp.delete("challenges")
async def on_delete_challenge(request):
    """Deletes challenge if permitted."""
    await Group.check_group_user_permissions(
        request, "challenges", request.args.get("group")
    )
    challenge = await Challenge.get_from_group(request)
    challenge.delete = True
    await challenge.save(update_fields="delete")
    return json("Challenge deleted.", challenge.json)


@social_bp.put("challenges/join")
@requires_authentication
async def on_join_challenge(request):
    """Join challenge and be added to its participants list."""
    challenge = await Challenge.get_from_group_and_member(
        request, request.ctx.authentication_session.bearer
    )
    await challenge.participants.add(request.ctx.authentication_session.bearer)
    return json("Challenge joined", challenge.json)


@social_bp.put("challenges/redeem")
@requires_authentication
async def on_challenge_redeem(request):
    """Adds user to finishers list if threshold attempt (e.g., "distance", "steps", "heartrate") exceeds challenge requirements."""
    challenge = await Challenge.get_from_participant(
        request, request.ctx.authentication_session.bearer
    )

    if challenge.has_expired():
        raise ChallengeExpiredError()
    elif challenge.threshold_type != request.args.get("threshold-type"):
        raise InvalidThresholdTypeError()
    elif request.args.get("threshold-attempt") > challenge.threshold:
        await challenge.finishers.add(request.ctx.authentication_session.bearer)
        return json("Challenge redeemed.", challenge.json)
    else:
        raise ThresholdNotMetError()
