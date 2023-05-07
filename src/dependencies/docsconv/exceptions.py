class BaseError(Exception):
    def __init__(self, message=None, errors=None, method=None, url=None):
        self.message = message
        if errors:
            message = ", ".join(errors)

        self.errors = errors
        self.method = method
        self.url = url

        super().__init__(message)

    def __str__(self):
        return f"{self.args[0]}, on {self.method} {self.url}"

    def getMessage(self):
        if self.errors is not None:
            return ", ".join(self.errors)
        return self.message


class InvalidRequest(BaseError):
    pass


class Unauthorized(BaseError):
    pass


class Forbidden(BaseError):
    pass


class InvalidPath(BaseError):
    pass


class RateLimitExceeded(BaseError):
    pass


class InternalServerError(BaseError):
    pass


class UnexpectedError(BaseError):
    pass


class BadGateway(BaseError):
    pass


class ParamValidationError(BaseError):
    pass
