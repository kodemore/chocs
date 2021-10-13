from examples.loading_modules.app import app
from chocs import serve

app.use("routes")
app.use("*.routes")

serve(app, port=8080, debug=True)
