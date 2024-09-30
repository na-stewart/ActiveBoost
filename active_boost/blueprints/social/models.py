import datetime

from sanic import Request
from sanic_security.authorization import check_permissions
from sanic_security.models import Account, AuthenticationSession
from tortoise import fields

from active_boost.common.models import BaseModel


class Challenge(BaseModel):
    title: str = fields.CharField(unique=True, max_length=225)
    description: str = fields.TextField()
    prize: int = fields.IntField()
    threshold = fields.IntField()  # Distance, steps, heartrate, etc.
    active: bool = fields.BooleanField(default=True)
    expiration_date: datetime.datetime = fields.DatetimeField()
    challenger: fields.ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account", null=True
    )  # If null, challenge is global. When created for group, set to group founder.
    participants: fields.ManyToManyRelation["Account"] = fields.ManyToManyField(
        "models.Account", through="challenge_participant"
    )

    @classmethod
    async def get_global(cls):
        """
        Create all global challenges not created by a user.
        """
        return await cls.filter(challenger=None, deleted=False).all()

    @classmethod
    async def get_from_challenger(cls, account: Account):
        """
        Retrieve all challenges created by the challenger.
        """
        return await cls.filter(challenger=account, deleted=False).all()

    @classmethod
    async def get_from_participant(cls, account: Account):
        """
        Retrieve all challenges that account is participating in.
        """
        return await cls.filter(participants__in=[account], deleted=False).all()


class Group(BaseModel):
    title: str = fields.CharField(unique=True, max_length=225)
    description: str = fields.TextField()
    private: bool = fields.BooleanField()
    disbanded: bool = fields.BooleanField()
    founder: fields.ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account"
    )
    members: fields.ManyToManyRelation["Account"] = fields.ManyToManyField(
        "models.Account", through="group_member"
    )
    challenges: fields.ManyToManyRelation["Challenge"] = fields.ManyToManyField(
        "models.Challenge", through="group_challenge"
    )

    @classmethod
    async def get_from_member(cls, account: Account):
        """
        Retrieve all challenges that account is participating in.
        """
        return await cls.filter(
            members__in=[account], deleted=False, disbanded=False
        ).all()

    @staticmethod
    async def check_group_user_permissions(
        request: Request, permissions: str
    ) -> AuthenticationSession:
        return await check_permissions(
            request, f"group-{request.args.get("group")}:{permissions}"
        )

    @property
    def json(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "private": self.private,
            "disbanded": self.disbanded,
            "founder": (
                self.founder.username if isinstance(self.founder, Account) else None
            ),
        }
