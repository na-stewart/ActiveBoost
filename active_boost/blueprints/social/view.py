from sanic import Blueprint
from sanic_security.authentication import requires_authentication
from sanic_security.authorization import (
    assign_role,
)
from sanic_security.models import Account, Role
from sanic_security.utils import get_expiration_date

from active_boost.blueprints.social.models import Group, Challenge
from active_boost.common.util import json, str_to_bool

social_bp = Blueprint("social")


@social_bp.get("groups/you")
@requires_authentication
async def on_get_user_groups(request):
    groups = await Group.get_from_member(request.ctx.authentication_session.bearer)
    return [group.json for group in groups]


@social_bp.get("groups")
async def on_get_all_public_groups(request):
    groups = await Group.filter(deleted=False, private=False).all()
    return [group.json for group in groups]


@social_bp.post("groups")
@requires_authentication
async def on_create_group(request):
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
    await Group.check_group_user_permissions(request, "group")
    group = await Group.get(id=request.args.get("id"), deleted=False)
    group.title = request.form.get("title")
    group.description = request.form.get("description")
    group.private = str_to_bool(request.form.get("private"))
    await group.save(update_fields=["title", "description", "private"])
    return json("Group updated.", group.json)


@social_bp.delete("groups")
async def on_delete_group(request):
    await Group.check_group_user_permissions(request, "group")
    group = await Group.get(id=request.args.get("id"), deleted=False)
    group.deleted = True
    await group.save(update_fields=["disbanded"])
    return json("Group disbanded.", group.json)


@social_bp.put("groups/join")
@requires_authentication
async def on_join_group(request):
    group = await Group.get(id=request.args.get("id"), deleted=False)
    await group.members.add(request.ctx.authentication_session.bearer)
    return json("You have joined this group!", group.json)


@social_bp.get("groups/role")
async def on_get_group_roles(request):
    await Group.check_group_user_permissions(request, "group")
    group = await Group.get(id=request.args.get("id"), deleted=False)
    roles = await Role.filter(
        permissions__startswith=f"group-{group.id}", deleted=False
    ).all()
    return json("Group roles retrieved.", [role.json for role in roles])


@social_bp.put("groups/role/assign")
async def on_permit_group_user(request):
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


@social_bp.put("groups/role/prohibit")
async def on_prohibit_group_user(request):
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


@social_bp.get("group/challenges/you")
@requires_authentication
async def on_get_user_challenges(request):
    challenges = await Challenge.get_from_participant(
        request.ctx.authentication_session.bearer
    )
    return [challenge.json for challenge in challenges]


@social_bp.get("groups/challenges")
@requires_authentication
async def on_get_group_challenges(request):
    challenges = await Challenge.get_all_from_group(request)
    return [challenge.json for challenge in challenges]


@social_bp.post("groups/challenges")
async def on_create_challenge(request):
    authentication_session = await Group.check_group_user_permissions(
        request, "challenges"
    )
    challenge = await Challenge.create(
        title=request.form.get("title"),
        description=request.form.get("description"),
        prize=request.form.get("prize"),
        threshold=request.form.get("threshold"),
        expiration_date=get_expiration_date(
            request.form.get("expiration-date")
        ),  # Change later.
        challenger=authentication_session.bearer,
        group=request.args.get("id"),
    )
    return json("Challenge created.", challenge.json)


@social_bp.put("groups/challenges")
async def on_update_challenge(request):
    await Group.check_group_user_permissions(request, "challenges")
    challenge = await Challenge.get_from_group(request)
    challenge.title = request.form.get("title")
    challenge.description = request.form.get("description")
    challenge.prize = request.form.get("prize")
    challenge.threshold = request.form.get("threshold")
    challenge.expiration_date = (
        get_expiration_date(request.form.get("expiration-date")),
    )  # Change later.
    await challenge.save(
        update_fields=[
            "title",
            "description",
            "prize",
            "threshold",
            "expiration_date",
        ]
    )
    return json("Challenge updated.", challenge.json)


@social_bp.delete("groups/challenges")
async def on_delete_challenge(request):
    await Group.check_group_user_permissions(request, "challenges")
    challenge = await Challenge.get_from_group(request)
    challenge.delete = True
    await challenge.save(update_fields="delete")
    return json("Challenge deleted.", challenge.json)
