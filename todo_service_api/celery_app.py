from todo_service_api.app import init_celery

app = init_celery()
app.conf.imports = app.conf.imports + ("todo_service_api.tasks.example",)
