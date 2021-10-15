from .http.http_error import HttpError, NotFoundError, BadRequestError


class ApplicationError(RuntimeError):
    @classmethod
    def for_invalid_namespace(cls, namespace: str) -> "ApplicationError":
        return ApplicationError(f"Failed to use namespace `{namespace}`")


__all__ = ["ApplicationError", "HttpError", "NotFoundError", "BadRequestError"]
