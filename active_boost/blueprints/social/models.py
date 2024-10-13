import datetime

from sanic import Request
from sanic_security.authorization import check_permissions
from sanic_security.models import Account, AuthenticationSession
from tortoise import fields

from active_boost.common.models import BaseModel


class Group(BaseModel):
    title: str = fields.CharField(unique=True, max_length=225)
    description: str = fields.TextField()
    private: bool = fields.BooleanField()
    founder: fields.ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account"
    )
    members: fields.ManyToManyRelation["Account"] = fields.ManyToManyField(
        "models.Account", through="group_member", related_name="memberships"
    )

    @classmethod
    async def get_all_from_member(cls, account: Account):
        """
        Retrieve all challenges that account is participating in.
        """
        return (
            await cls.filter(members__in=[account], deleted=False)
            .prefetch_related("members")
            .all()
        )

    @classmethod
    async def get_from_member(cls, request: Request, account: Account):
        """
        Retrieve all challenges that account is participating in.
        """
        return await cls.get(
            id=request.args.get("id"),
            members__in=[account],
            deleted=False,
        )

    @staticmethod
    async def check_group_user_permissions(
        request: Request, permissions: str
    ) -> AuthenticationSession:
        return await check_permissions(
            request, f"group-{request.args.get("id")}:{permissions}"
        )

    @property
    def json(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "private": self.private,
            "founder": (
                self.founder.username if isinstance(self.founder, Account) else None
            ),
        }


class Challenge(BaseModel):
    title: str = fields.CharField(unique=True, max_length=225)
    description: str = fields.TextField()
    reward: int = fields.IntField()
    penalty: int = fields.IntField()
    threshold = fields.IntField()  # Distance, steps, heartrate, etc.
    threshold_type = fields.CharField(max_length=255)
    expiration_date: datetime.datetime = fields.DatetimeField()
    challenger: fields.ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account", null=True, related_name="challenged_by"
    )
    group: fields.ForeignKeyRelation["Group"] = fields.ForeignKeyField(
        "models.Group", null=True
    )
    participants: fields.ManyToManyRelation["Account"] = fields.ManyToManyField(
        "models.Account",
        through="challenge_participant",
    )
    finishers: fields.ManyToManyRelation["Account"] = fields.ManyToManyField(
        "models.Account", through="challenge_finisher", related_name="finisher"
    )

    @property
    def json(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "reward": self.reward,
            "penalty": self.penalty,
            "completion_threshold": self.threshold,
            "threshold_type": self.threshold_type,
            "group": self.group.title if isinstance(self.group, Group) else None,
        }

    def has_expired(self):
        return datetime.datetime.now(datetime.timezone.utc) >= self.expiration_date

    @classmethod
    async def get_from_challenger(cls, account: Account):
        """
        Retrieve all challenges created by the challenger.
        """
        return await cls.filter(challenger=account, deleted=False).all()

    @classmethod
    async def get_all_from_participant(cls, account: Account):
        """
        Retrieve all challenges that account is participating in.
        """
        return await cls.filter(participants__in=[account], deleted=False).all()

    @classmethod
    async def get_from_participant(cls, request: Request, account: Account):
        """
        Retrieve all challenges that account is participating in.
        """
        return await cls.get(
            id=request.args.get("id"),
            participants__in=[account],
            deleted=False,
        )

    @classmethod
    async def get_all_from_group(cls, request: Request):
        """
        Retrieve all challenges that account is participating in.
        """
        return await cls.filter(
            group=request.args.get("id"),
            deleted=False,
        ).all()

    @classmethod
    async def get_from_group(cls, request: Request):
        """
        Retrieve all challenges that account is participating in.
        """
        return await Challenge.get(
            id=request.args.get("challenge"),
            group=request.args.get("id"),
            deleted=False,
        )
