from tortoise import fields

from active_boost.common.models import BaseModel


class Account(BaseModel):
    """
    Contains all identifiable user information.

    Attributes:
        username (str): Public identifier.
        bio (str): A small excerpt about the user.
        user_id (str): Obtained via OAuth during login.
        disabled (bool): Renders the account unusable.
    """

    bio: str = fields.TextField(null=True, default="")
    user_id: str = fields.CharField(max_length=255, unique=True)
    username: str = fields.CharField(max_length=255)
    disabled: bool = fields.BooleanField(default=False)

    @property
    def json(self) -> dict:
        return {
            "date_created": str(self.date_created),
            "date_updated": str(self.date_updated),
            "id": self.id,
            "fitbit_id": self.user_id,
            "username": self.username,
            "pfp_url": self.icon_url,
            "bio": self.bio,
        }
