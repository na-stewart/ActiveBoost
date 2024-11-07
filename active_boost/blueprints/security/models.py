from tortoise import fields

from active_boost.common.models import BaseModel


class Account(BaseModel):
    """
    Contains all identifiable user information.

    Attributes:
        username (str): Public identifier.
        bio (str): A small excerpt about the user.
        user_id (str): Obtained via OAuth during login.
        roles (ManyToManyRelation[Role]): Roles associated with this account.
        disabled (bool): Renders the account unusable.
    """

    bio: str = fields.TextField(null=True)
    user_id: str = fields.CharField(max_length=255, unique=True)
    username: str = fields.CharField(max_length=255, unique=True)
    roles: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
        "models.Role", through="account_role"
    )
    disabled: bool = fields.BooleanField(default=False)

    @property
    def json(self) -> dict:
        return {
            "username": self.username,
            "pfp_url": self.icon_url,
            "bio": self.bio,
        }


class Role(BaseModel):
    """
    Assigned to an account to authorize an action.

    Attributes:
        name (str): Name of the role.
        description (str): Description of the role.
        permissions (str): Permissions of the role. Must be separated via comma + space and in wildcard format.
    """

    name: str = fields.CharField(unique=True, max_length=255)
    description: str = fields.CharField(max_length=255, null=True)
    permissions: str = fields.CharField(max_length=255, null=True)

    @property
    def json(self) -> dict:
        return {
            "id": self.id,
            "date_created": str(self.date_created),
            "date_updated": str(self.date_updated),
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions.split(":")[1],
        }
