from sanic import SanicException

from active_boost.common.util import json


class ActiveBoostError(SanicException):
    def __init__(self, message: str, code: int):
        self.json = json(message, self.__class__.__name__, code)
        super().__init__(message, 400)


class ThresholdNotMetError(ActiveBoostError):
    def __init__(
        self,
        message: str = "User threshold attempt must exceed challenge completion threshold.",
    ):
        super().__init__(message)
