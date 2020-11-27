import os

from chocs import create_wsgi_handler
from chocs import serve

from .handler import *

app = create_wsgi_handler(debug=True)

if __name__ == "__main__":
    print("Running server on port 8080")
    serve(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        debug=True
    )
