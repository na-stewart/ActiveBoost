from sanic import Blueprint
from sanic_security.authentication import requires_authentication
from sanic_security.authorization import (
    require_permissions,
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


@social_bp.get("groups/all")
@require_permissions("groups:get")
async def on_get_all_groups(request):
    groups = await Group.filter(deleted=False).all()
    return [group.json for group in groups]


@social_bp.get("groups/all/public")
async def on_get_all_public_groups(request):
    groups = await Group.filter(deleted=False, disbanded=False, private=False).all()
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
    await assign_role(
        f"{group.title} Founder",
        request.ctx.authentication_session.bearer,
        f"group-{group.id}:*",
        f"Has complete control over {group.title}.",
    )
    return json("Group created.", group.json)


@social_bp.put("groups")
async def on_update_group(request):
    await Group.check_group_user_permissions(request, "update")
    group = await Group.get(
        id=request.args.get("group"), disbanded=False, deleted=False
    )
    group.title = request.form.get("title")
    group.description = request.form.get("description")
    group.private = str_to_bool(request.form.get("private"))
    await group.save(update_fields=["title", "description", "private"])
    return json("Group updated.", group.json)


@social_bp.post("groups/join")
@requires_authentication
async def on_join_group(request):
    group = await Group.get(
        id=request.args.get("group"), disbanded=False, deleted=False
    )
    await group.members.add(request.ctx.authentication_session.bearer)
    return json("You have joined this group!", group.json)


@social_bp.put("groups/disband")
async def on_disband_group(request):
    await Group.check_group_user_permissions(request, "update")
    group = await Group.get(
        id=request.args.get("group"), disbanded=False, deleted=False
    )
    group.disbanded = True
    await group.save(update_fields=["disbanded"])
    return json("Group disbanded.", group.json)


@social_bp.delete("groups")
@require_permissions("group:delete")
async def on_delete_group(request):
    group = await Group.get(id=request.args.get("group"), deleted=False)
    group.deleted = True
    await group.save(update_fields=["deleted"])
    return json("Group deleted.", group.json)


@social_bp.post("groups/role")
async def on_create_group_prole(request):
    await Group.check_group_user_permissions(request, "roles")
    group = await Group.get(
        id=request.args.get("group"), disbanded=False, deleted=False
    )
    role = await Role.create(
        name=request.form.get("name"),
        permissions=f"group-{group.id}:{request.form.get("perms")}",
        description=request.form.get("description"),
    )
    return json("Group role created.", role.json)


@social_bp.get("groups/role")
async def on_get_group_roles(request):
    await Group.check_group_user_permissions(request, "roles")
    group = await Group.get(
        id=request.args.get("group"), disbanded=False, deleted=False
    )
    roles = await Role.filter(
        permissions__startswith=f"group-{group.id}", deleted=False
    ).all()
    return json("Group roles retrieved.", [role.json for role in roles])


@social_bp.post("groups/role/assign")
async def on_permit_group_user(request):
    await Group.check_group_user_permissions(request, "perms")
    group = await Group.get(
        id=request.args.get("group"), disbanded=False, deleted=False
    )
    account_being_permitted = await Account.get(
        id=request.args.get("account"), deleted=False
    )
    role = await Role.get(
        permissions__startswith=f"group-{group.id}",
        id=request.args.get("role"),
        deleted=False,
    )
    await account_being_permitted.roles.add(role)
    return json("Group participant assigned role.", role.json)


@social_bp.delete("groups/role/prohibit")
async def on_prohibit_group_user(request):
    await Group.check_group_user_permissions(request, "perms")
    group = await Group.get(
        id=request.args.get("group"), disbanded=False, deleted=False
    )
    account_being_permitted = await Account.get(
        id=request.args.get("account"), deleted=False
    )
    role = await Role.get(
        permissons__startswith=f"group-{group.id}",
        id=request.args.get("role"),
        deleted=False,
    )
    await account_being_permitted.roles.remove(role)
    return json("Group participant role removed.", role.json)


@social_bp.get("challenges")
@require_permissions("challenges:get")
async def on_get_all_challenges(request):
    challenges = await Challenge.filter(deleted=False).all()
    return [challenge.json for challenge in challenges]


@social_bp.get("challenges/you")
@requires_authentication
async def on_get_user_challenges(request):
    challenges = await Challenge.get_from_participant(
        request.ctx.authentication_session.bearer
    )
    return [challenge.json for challenge in challenges]


@social_bp.get("challenges/group")
@requires_authentication
async def on_get_group_challenges(request):
    group, challenges_queryset = await Challenge.get_queryset_from_group(request)
    challenges = await challenges_queryset.filter(deleted=False, active=True).all()
    return [challenge.json for challenge in challenges]


@social_bp.post("challenges")
async def on_create_challenge(request):
    authentication_session = await Group.check_group_user_permissions(
        request, "challenges"
    )
    group = await Group.get(
        id=request.args.get("group"), disbanded=False, deleted=False
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
    )
    await group.challenges.add(challenge)
    return json("Challenge created.", challenge.json)


@social_bp.put("challenge")
async def on_update_challenge(request):
    await Group.check_group_user_permissions(request, "challenges")
    group, challenges_queryset = await Challenge.get_queryset_from_group(request)
    challenge = challenges_queryset.get(
        id=request.args.get("challenge"), deleted=False, active=True
    )
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


@social_bp.put("groups/deactivate")
async def on_deactivate_challenge(request):
    await Group.check_group_user_permissions(request, "challenges")
    group, challenges_queryset = await Challenge.get_queryset_from_group(request)
    challenge = await challenges_queryset.get(
        id=request.args.get("challenge"), deleted=False, active=True
    )
    challenge.active = False
    await challenge.save(update_fields="active")
    return json("Challenge deactivated.", challenge.json)


@social_bp.delete("challenges")
@require_permissions("challenges:delete")
async def on_delete_challenge(request):
    challenge = await Challenge.get(id=request.args.get("group"), deleted=False)
    challenge.deleted = True
    await challenge.save(update_fields=["deleted"])
    return json("Challenge deleted.", challenge.json)
