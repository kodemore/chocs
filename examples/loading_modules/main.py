from app import app
from chocs import serve

app.use("routes")

serve(app, port=8080, debug=True)
