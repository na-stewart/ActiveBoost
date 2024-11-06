from sanic import Blueprint

from active_boost.blueprints.challenge.models import Challenge
from active_boost.blueprints.group.models import Group
from active_boost.blueprints.security.common import require_permissions, assign_role
from active_boost.blueprints.security.models import Role, Account
from active_boost.common.util import json, str_to_bool

group_bp = Blueprint("group", url_prefix="group")


@group_bp.get("group/you")
async def on_get_user_groups(request):
    """Retrieves groups associated with user."""
    groups = await Group.get_all_from_member(request.ctx.authentication_session.bearer)
    return json("User groups retrieved.", [group.json for group in groups])


@group_bp.get("group/members")
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
        response_array.append(
            {
                "account": member.username,
                "balance": group_balance,
            }
        )

    return json("Group members retrieved.", response_array)


@group_bp.get("group")
async def on_get_all_public_groups(request):
    """Retrieves all groups not marked as private."""
    groups = await Group.filter(deleted=False, private=False).all()
    return json("Public groups retrieved.", [group.json for group in groups])


@group_bp.post("group")
async def on_create_group(request):
    """Creates a group and are assigned all permissions for that group to allow full access."""
    group = await Group.create(
        title=request.form.get("title"),
        description=request.form.get("description"),
        private=str_to_bool(request.form.get("private")),
        founder=request.ctx.authentication_session.bearer,
    )
    await group.members.add(request.ctx.authentication_session.bearer)
    await assign_role(
        f"{group.title} Manager",
        group.id,
        request.ctx.account,
        f"group-{group.id}:*",
        f"Has complete control over {group.title}.",
    )
    return json("Group created.", group.json)


@group_bp.put("group")
@require_permissions("group:update")
async def on_update_group(request):
    """Update group information if permitted."""
    group = await Group.get(id=request.args.get("id"), deleted=False)
    group.title = request.form.get("title")
    group.description = request.form.get("description")
    group.private = str_to_bool(request.form.get("private"))
    await group.save(update_fields=["title", "description", "private"])
    return json("Group updated.", group.json)


@group_bp.delete("group")
@require_permissions("group:delete")
async def on_delete_group(request):
    group = await Group.get(id=request.args.get("id"), deleted=False)
    group.deleted = True
    await group.save(update_fields=["disbanded"])
    return json("Group deleted.", group.json)


@group_bp.put("group/join")
async def on_join_group(request):
    """Join group and be added to its members list."""
    group = await Group.get(id=request.args.get("id"), deleted=False)
    await group.members.add(request.ctx.authentication_session.bearer)
    return json("Group joined.", group.json)


@group_bp.get("group/roles")
@require_permissions("group:roles")
async def on_get_group_roles(request):
    """Retrieve group roles and view details if permitted."""
    roles = await Role.filter(
        permissions__startswith=f"group-{request.args.get("id")}", deleted=False
    ).all()
    return json("Group roles retrieved.", [role.json for role in roles])


@group_bp.put("group/roles/assign")
@require_permissions("group:roles")
async def on_permit_group_user(request):
    """User can add role to another account such as moderator, manager, etc."""
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


@group_bp.put("group/roles/prohibit")
@require_permissions("group:roles")
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
