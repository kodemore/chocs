import os

from app import app
from handler import *

from chocs import serve

if __name__ == "__main__":
    print("Running server on port 8080")
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
