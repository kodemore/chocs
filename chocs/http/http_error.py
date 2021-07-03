class HttpError(Exception):
    status_code: int = 500
    http_message = "Internal Server Error"

    def __str__(self) -> str:
        return self.http_message

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.status_code}, {self.http_message})"


class NotFoundError(HttpError):
    status_code: int = 404
    http_message = "Not Found"


class BadRequestError(HttpError):
    status_code: int = 400
    http_message = "Bad Request"


__all__ = ["HttpError", "NotFoundError", "BadRequestError"]
