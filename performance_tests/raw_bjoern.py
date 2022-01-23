from io import BytesIO
from typing import Dict, Any, Callable

import bjoern


def app(environ: Dict[str, Any], start: Callable) -> BytesIO:
    body = BytesIO()
    body.write(b"OK")

    headers = {
        "test": "1",
    }

    start(
        str(200),
        [(key, value) for key, value in headers.items()],
    )

    body.seek(0)
    return body


bjoern.run(app, "127.0.0.1", 8080)
