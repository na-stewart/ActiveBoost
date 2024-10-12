from sanic_security.models import Account
from tortoise import fields

from active_boost.common.models import BaseModel


class Profile(BaseModel):
    account: fields.ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account",
    )
    pfp_url: str = fields.CharField(max_length=255, null=True)
    bio: str = fields.TextField(null=True)
    balance: int = fields.IntField()

    @classmethod
    async def get_from_account(cls, account: Account):
        profile = await cls.get(account=account, deleted=False)
        return profile

    @classmethod
    async def update_balance(cls, account: Account, adjustment: int):
        profile = await cls.get_from_account(account)
        profile.balance += adjustment
        await profile.save(update_fields=["balance"])
        return profile

    @property
    def json(self) -> dict:
        return {
            "id": self.id,
            "pfp_url": self.pfp_url,
            "balance": self.balance,
            "bio": self.bio,
            "account": (
                self.account.username if isinstance(self.account, Account) else None
            ),
        }
