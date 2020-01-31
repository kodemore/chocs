class HttpError(Exception):
    status_code: int = 500
    http_message = "Internal Server Error"

    def __init__(self, http_message: str, status_code: int = None):
        if status_code:
            self.status_code = status_code
        if http_message:
            self.http_message = http_message

        super().__init__(http_message)


__all__ = ["HttpError"]
