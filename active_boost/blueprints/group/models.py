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
