class HttpError(Exception):
    status_code: int = 500
    http_message = "Internal Server Error"

    def __str__(self) -> str:
        return self.http_message

    def __repr__(self) -> str:
        return self.__class__.__name__ + f"({self.status_code}, {self.http_message})"


__all__ = ["HttpError"]
