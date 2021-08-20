from io import BytesIO
from typing import Union


def write_body(
    body: BytesIO,
    contents: Union[str, bytes, bytearray, BytesIO],
    encoding: str = "utf8",
) -> None:
    if isinstance(contents, str):
        body.write(contents.encode(encoding))
    elif isinstance(contents, BytesIO):
        contents.seek(0)
        body.write(contents.read())
    else:
        body.write(contents)
