from sanic_security.models import Account
from tortoise import fields

from active_boost.common.models import BaseModel


class Profile(BaseModel):
    account: fields.ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account",
    )
    pfp_url: str = fields.CharField(max_length=255, null=True)
    bio: str = fields.TextField(null=True)

    @classmethod
    async def get_from_account(cls, account: Account):
        profile = await cls.get(account=account, deleted=False)
        return profile

    @property
    def json(self) -> dict:
        return {
            "pfp_url": self.pfp_url,
            "bio": self.bio,
        }
