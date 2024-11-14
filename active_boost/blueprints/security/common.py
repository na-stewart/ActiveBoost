import functools
from fnmatch import fnmatch

from sanic.response.types import Request

from active_boost.common.exceptions import AuthorizationError


async def check_permissions(
    request: Request, group_id: int, *required_permissions: str
):
    """Determines if the account has sufficient permissions for an action."""
    roles = await request.ctx.account.roles.filter(
        permissions__startswith=f"group-{group_id}", deleted=False
    ).all()
    for role in roles:
        for required_permission, role_permission in zip(
            required_permissions, role.permissions.split(", ")
        ):
            if fnmatch(f"group-{group_id}:{required_permission}", role_permission):
                return
    raise AuthorizationError()


def require_permissions(*required_permissions: str):
    """Determines if the account has sufficient permissions for an action."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request, *args, **kwargs):
            await check_permissions(
                request,
                request.args.get("group") or request.args.get("id"),
                *required_permissions,
            )
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
