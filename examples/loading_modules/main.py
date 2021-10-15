from examples.loading_modules.app import app
from chocs import serve

app.use("examples.loading_modules.routes")
app.use("examples.loading_modules.*.routes")

serve(app, port=8080, debug=True)
