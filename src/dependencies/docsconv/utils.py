import json
from . import exceptions


def raise_for_error(method, url, status_code, message=None, errors=None):
    """Helper method to raise exceptions based on the status code of a response received back from Vault.
    :param method: HTTP method of a request to Vault.
    :type method: str
    :param url: URL of the endpoint requested in Vault.
    :type url: str
    :param status_code: Status code received in a response from Vault.
    :type status_code: int
    :param message: Optional message to include in a resulting exception.
    :type message: str
    :param errors: Optional errors to include in a resulting exception.
    :type errors: list | str
    :raises: exceptions.InvalidRequest | exceptions.Unauthorized | exceptions.Forbidden |
        exceptions.InvalidPath | exceptions.RateLimitExceeded | exceptions.InternalServerError |
        exceptions.BadGateway | exceptions.UnexpectedError
    """
    if status_code == 400:
        raise exceptions.InvalidRequest(
            message, errors=errors, method=method, url=url)
    elif status_code == 401:
        raise exceptions.Unauthorized(
            message, errors=errors, method=method, url=url)
    elif status_code == 403:
        raise exceptions.Forbidden(
            message, errors=errors, method=method, url=url)
    elif status_code == 404:
        raise exceptions.InvalidPath(
            message, errors=errors, method=method, url=url)
    elif status_code == 429:
        raise exceptions.RateLimitExceeded(
            message, errors=errors, method=method, url=url
        )
    elif status_code == 500:
        raise exceptions.InternalServerError(
            message, errors=errors, method=method, url=url
        )
    elif status_code == 502:
        raise exceptions.BadGateway(
            message, errors=errors, method=method, url=url)
    else:
        raise exceptions.UnexpectedError(
            message or errors, method=method, url=url)


def raise_for_response(method, url, res):
    errors = []
    text = ''
    if "application/json" in res.getheader("Content-Type"):
        try:
            r = json.loads(res.data.decode('utf-8'))
            errors = [r['message']]
            text = r['message']
        except Exception:
            pass

        if errors is None:
            text = res.text
        raise_for_error(
            method, url, res.status, text, errors=errors
        )
