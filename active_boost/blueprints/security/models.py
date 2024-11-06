from tortoise import fields

from active_boost.common.models import BaseModel


class Account(BaseModel):
    bio: str = fields.TextField(null=True)
    user_id: str = fields.CharField(max_length=255, unique=True)
    username: str = fields.CharField(max_length=255, unique=True)
    roles: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
        "models.Role", through="account_role"
    )

    @property
    def json(self) -> dict:
        return {
            "username": self.username,
            "pfp_url": self.icon_url,
            "bio": self.bio,
        }


class Role(BaseModel):
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
