from sanic import SanicException

from active_boost.common.util import json


class ActiveBoostError(SanicException):
    def __init__(self, message: str, code: int = 400):
        self.json = json(message, self.__class__.__name__, code)
        super().__init__(message, code)


class ThresholdNotMetError(ActiveBoostError):
    def __init__(self):
        super().__init__(
            "User threshold attempt must exceed challenge completion threshold."
        )


class ChallengeExpiredError(ActiveBoostError):
    def __init__(self):
        super().__init__("This challenge has expired and can no longer be redeemed.")
