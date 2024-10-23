from sanic import SanicException

from active_boost.common.util import json


class ActiveBoostError(SanicException):
    """
    General Active Boost exception.
    """

    def __init__(self, message: str, code: int = 400):
        self.json = json(message, self.__class__.__name__, code)
        super().__init__(message, code)


class ThresholdNotMetError(ActiveBoostError):
    """
    Raised when user heartrate, steps, etc total does not meet challenge requirements.
    """

    def __init__(self):
        super().__init__(
            "User threshold attempt must exceed challenge completion threshold."
        )


class InvalidThresholdTypeError(ActiveBoostError):
    """
    Raised when user threshold type is incorrect.
    """

    def __init__(self):
        super().__init__("User threshold type does not match challenge threshold type.")


class ChallengeExpiredError(ActiveBoostError):
    """
    Raised when challenge expiration date has exceeded current date.
    """

    def __init__(self):
        super().__init__("This challenge has expired and can no longer be redeemed.")
