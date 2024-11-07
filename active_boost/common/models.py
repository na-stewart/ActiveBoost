import datetime
from os import environ

import httpx
from sanic.utils import str_to_bool
from tortoise import fields, Model


class BaseModel(Model):
    """
    Base model that all other models derive from.

    Attributes:
        id (int): Primary key of model.
        icon_url (string): A majority of models will have an icon in some way, url of icon file.
        date_created (datetime): Time this model was created in the database.
        date_updated (datetime): Time this model was updated in the database.
        deleted (bool): Renders the model filterable without removing from the database.
    """

    id: int = fields.IntField(pk=True)
    icon_url: str = fields.CharField(null=True, max_length=255)
    date_created: datetime.datetime = fields.DatetimeField(auto_now_add=True)
    date_updated: datetime.datetime = fields.DatetimeField(auto_now=True)
    deleted: bool = fields.BooleanField(default=False)

    @property
    def json(self) -> dict:
        raise NotImplementedError()

    class Meta:
        abstract = True


class Config(dict):
    DEBUG: bool
    SECRET: str
    DATABASE_URL: str
    GENERATE_SCHEMAS: bool
    APP_BUILD: str
    FITBIT_SECRET: str
    FITBIT_CLIENT: str

    def load_environment_variables(self, load_env="ACTIVEBOOST_") -> None:
        """
        Any environment variables defined with the prefix argument will be applied to the config.
        Args:
            load_env (str): Prefix being used to apply environment variables into the config.
        """
        for key, value in environ.items():
            if not key.startswith(load_env):
                continue

            _, config_key = key.split(load_env, 1)

            for converter in (int, float, str_to_bool, str):
                try:
                    self[config_key] = converter(value)
                    break
                except ValueError:
                    pass

    def __init__(self, default_config: dict):
        super().__init__(default_config)
        self.__dict__ = self
        self.load_environment_variables()


class BearerAuth(httpx.Auth):
    def __init__(self, token):
        self.token = token

    def auth_flow(self, request):
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request
