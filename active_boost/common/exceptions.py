from sanic import SanicException

from active_boost.common.util import json, resource_options


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

    def __init__(self, message):
        super().__init__(message)


class InvalidThresholdTypeError(ActiveBoostError):
    """
    Raised when user threshold type is incorrect.
    """

    def __init__(self):
        super().__init__(
            f"Threshold type is invalid, must be {', '.join(resource_options)}."
        )


class ChallengeExpiredError(ActiveBoostError):
    """
    Raised when challenge expiration date has exceeded current date.
    """

    def __init__(self):
        super().__init__("This challenge has expired and can no longer be redeemed.")


class AuthorizationError(ActiveBoostError):
    """
    Raised when an account has insufficient permissions for an action.
    """

    def __init__(self, message="Insufficient permissions required for this action."):
        super().__init__(message, 403)


class AnonymousUserError(ActiveBoostError):
    """
    Raised when an account has not logged in.
    """

    def __init__(self):
        super().__init__("Login required.", 401)
