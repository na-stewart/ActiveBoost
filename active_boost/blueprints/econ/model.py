from sanic_security.models import Account
from tortoise import fields

from active_boost.common.models import BaseModel


class Transaction(BaseModel):
    transactor: fields.ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account", null=True
    )  # The account giving or redacting points. Null for system transactions.
    transactee: fields.ForeignKeyRelation["Account"] = fields.ForeignKeyField(
        "models.Account"
    )  # The account receiving or losing points.
    description: str = fields.TextField()
    value: int = fields.IntField()
