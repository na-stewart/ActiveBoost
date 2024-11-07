import datetime

from sanic.response.types import Request
from tortoise import fields

from active_boost.blueprints.security.models import Account
from active_boost.common.models import BaseModel


class Group(BaseModel):
    """
    Base Sanic Security model that all other models derive from.

    Attributes:
        title (str): Title of the group, must be unique and have a maximum length of 225 characters.
        description (str): Detailed description of the group.
        private (bool): Indicates if the group is viewable for all users or only members.
        date_updated (datetime): The last time this model was updated in the database.
        deleted (bool): Soft delete flag, makes the model filterable without removing it from the database.
        founder (ForeignKeyRelation["Account"]): The account that created the group. Foreign key to the Account model.
        members (ManyToManyRelation["Account"]): A list of accounts that are members of the group. This is a many-to-many relation, linked through a join table "group_member".


    """

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
        """Retrieve all groups account has joined."""
        return (
            await cls.filter(members__in=[account], deleted=False)
            .prefetch_related("members")
            .all()
        )

    @classmethod
    async def get_from_member(
        cls, request: Request, account: Account, group_id: int = None
    ):
        """Retrieve particular group account has joined."""
        return await cls.get(
            id=group_id if group_id else request.args.get("id"),
            members__in=[account],
            deleted=False,
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
    """
    Attributes:
        title (str): Title of the challenge.
        description (str): Detailed description of the challenge, describe activities and their difficulty.
        reward (int): The amount of points a user receives associated with completing the challenge.
        threshold (int): The target value for the challenge (e.g., distance, steps, heart rate).
        threshold_type (str): A description of the metric being measured for the threshold (e.g., "distance", "steps", "heartrate").
        expiration_date (datetime): The deadline by which the challenge must be completed.
        challenger (ForeignKeyRelation["Account"]): The account that issued the challenge. Can be null if not set. Foreign key to the Account model.
    """

    title: str = fields.CharField(unique=True, max_length=225)
    description: str = fields.TextField()
    reward: int = fields.IntField()
    threshold = fields.IntField()
    threshold_type = fields.CharField(
        max_length=255
    )  # Distance, steps, heartrate, etc.
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
            "completion_threshold": self.threshold,
            "threshold_type": self.threshold_type,
            "expiration_date": str(self.expiration_date),
            "group": self.group.title if isinstance(self.group, Group) else None,
        }

    def has_expired(self):
        """Checks if current time has passed challenge expiration."""
        return datetime.datetime.now(datetime.timezone.utc) >= self.expiration_date

    @classmethod
    async def get_from_challenger(cls, account: Account):
        """Retrieve all challenges created by the challenger."""
        return await cls.filter(challenger=account, deleted=False).all()

    @classmethod
    async def get_all_from_participant(cls, account: Account):
        """Retrieve all challenges that account is participating in."""
        return await cls.filter(participants__in=[account.id], deleted=False).all()

    @classmethod
    async def get_from_participant(cls, request: Request, account: Account):
        """Retrieves particular challenge associated with participant."""
        return await cls.get(
            id=request.args.get("id"),
            participants__in=[account],
            deleted=False,
        )

    @classmethod
    async def get_all_from_group(cls, request: Request, group_id: int = None):
        """Retrieve all challenges associated with group."""
        return await cls.filter(
            group=group_id if group_id else request.args.get("group"),
            deleted=False,
        ).all()

    @classmethod
    async def get_all_from_group_and_member(cls, request: Request, account: Account):
        """Retrieve all challenges associated with a group that the account is a member in."""
        group = await Group.get_from_member(request, account, request.args.get("group"))
        return await cls.filter(
            group=group,
            deleted=False,
            participants__in=[account],
        ).all()

    @classmethod
    async def get_from_group(cls, request: Request):
        """Retrieve particular challenge associated with group."""
        return await Challenge.get(
            id=request.args.get("id"),
            group=request.args.get("group"),
            deleted=False,
        )

    @classmethod
    async def get_from_group_and_member(cls, request: Request, account: Account):
        """Retrieve particular challenge associated with a group that the account is a member in."""
        group = await Group.get_from_member(request, account, request.args.get("group"))
        return await Challenge.get(
            id=request.args.get("id"),
            group=group,
            deleted=False,
        )
