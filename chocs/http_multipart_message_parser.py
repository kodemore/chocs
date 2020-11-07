from cgi import parse_header
from enum import Enum
from tempfile import TemporaryFile
from typing import Any
from typing import Dict
from typing import IO
from typing import Tuple


class UploadedFile:
    """
    Proxy class for TemporaryFile (uploaded file)
    """

    def __init__(self, file: IO[Any], mimetype: str, filename: str):
        self.file = file
        self.mimetype = mimetype
        self.filename = filename
        self.length = 0
        self._str = ""

    def read(self) -> bytes:
        return self.file.read()

    def seek(self, offset: int) -> int:
        return self.file.seek(offset)

    def close(self) -> None:
        self.file.close()

    def save(self, path: str) -> IO[Any]:
        if self.file.closed:
            raise ValueError(f"Cannot save to file {path} of closed stream.")
        with open(path, "wb") as file:
            self.seek(0)
            file.write(self.read())

        return file

    def __float__(self) -> None:
        raise ValueError(
            f"Cannot convert instance of {TemporaryFile.__name__} to float"
        )

    def __int__(self) -> None:
        raise ValueError(f"Cannot convert instance of {TemporaryFile.__name__} to int")

    def __len__(self) -> int:
        if not self.length:
            read_bytes = self.read()
            self.seek(0)
            self.length = len(read_bytes)
        return self.length

    def __bool__(self) -> bool:
        return len(self) > 0

    def __str__(self) -> str:

        if not self._str:
            self._str = self.read().decode()

        return self._str

    def __enter__(self) -> IO[Any]:
        return self.file

    def __exit__(self, *args: Any) -> None:
        self.close()


class ParserState(Enum):
    PART_BOUNDARY = 0
    CONTENT_DISPOSITION = 1
    CONTENT_TYPE = 2
    CONTENT_HEADER = 3
    CONTENT_DATA = 4
    END = 5


def parse_multipart_message(
    data: bytes,
    boundary: str,
    encoding: str = "utf8"
) -> Dict[str, Any]:
    state = ParserState.PART_BOUNDARY
    prev_byte = None
    cursor = 0
    boundary_length = len(boundary)
    string_buffer = ""
    body = {}

    def _append_content_to_body(
            raw_content_disposition: str, _content_type: str, _content_data: bytes
    ) -> None:
        parsed_content_disposition: Tuple[str, Dict[str, str]] = parse_header(
            raw_content_disposition[20:]
        )
        if "filename" in parsed_content_disposition[1]:
            tmp_file = TemporaryFile()
            tmp_file.write(_content_data)
            tmp_file.seek(0)
            body[parsed_content_disposition[1]["name"]] = UploadedFile(
                tmp_file,
                _content_type[14:].lower(),
                parsed_content_disposition[1]["filename"],
            )
        else:
            body[parsed_content_disposition[1]["name"]] = _content_data.decode(encoding)

    content_disposition = ""
    content_type = ""
    content_cursor = 0

    for code in data:
        line_break = code == 0x0A and prev_byte == 0x0D
        new_line_char = code == 0x0A or code == 0x0D

        if not new_line_char:
            string_buffer = string_buffer + chr(code)

        if state is ParserState.PART_BOUNDARY and line_break:
            if string_buffer == "--" + boundary:
                string_buffer = ""
                state = ParserState.CONTENT_DISPOSITION
            else:
                raise IOError(
                    "Could not parse message body, body is malformed or incorrect boundary was passed."
                )

        elif state is ParserState.CONTENT_DISPOSITION and line_break:
            content_disposition = string_buffer
            string_buffer = ""
            state = ParserState.CONTENT_TYPE
            if (
                data[cursor + 1 : cursor + 13].decode(encoding).lower()
                != "content-type"
            ):
                state = ParserState.CONTENT_HEADER
        elif state is ParserState.CONTENT_TYPE and line_break:
            content_type = string_buffer
            state = ParserState.CONTENT_HEADER
            string_buffer = ""
        elif state is ParserState.CONTENT_HEADER and line_break:
            string_buffer = ""
            state = ParserState.CONTENT_DATA
            content_cursor = cursor
        if state is ParserState.CONTENT_DATA:
            if line_break and string_buffer == "--" + boundary:
                content_data = data[content_cursor + 1 : cursor - (boundary_length + 5)]
                _append_content_to_body(content_disposition, content_type, content_data)
                content_type = ""
                state = ParserState.CONTENT_DISPOSITION

            if line_break and string_buffer == "--" + boundary + "--":
                content_data = data[content_cursor + 1 : cursor - (boundary_length + 7)]
                _append_content_to_body(content_disposition, content_type, content_data)
                content_type = ""
                state = ParserState.END

            if line_break:
                string_buffer = ""

        prev_byte = code
        cursor += 1

    return body


__all__ = ["UploadedFile", "parse_multipart_message"]
