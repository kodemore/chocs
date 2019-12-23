from .http_error import HttpError


class NotFoundError(HttpError):
    status_code: int = 404
    http_message = "Not Found"


__all__ = ["NotFoundError"]
