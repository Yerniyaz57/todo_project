from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from todo_service_api.api.schemas import TaskSchema
from todo_service_api.models import Task
from todo_service_api.extensions import db
from todo_service_api.commons.pagination import paginate
from todo_service_api.tasks.example import send_email_all_user


class TaskListResources(Resource):
    method_decorators = [jwt_required]

    def get(self):
        tasks = Task.query
        schema = TaskSchema(exclude=['description'], many=True)
        return paginate(tasks, schema)

    def post(self):
        schema = TaskSchema(exclude=['done'])
        task = schema.load(request.json)
        db.session.add(task)
        db.session.commit()
        return {"msg": "task created", "task": schema.dump(task)}, 201


class TaskResource(Resource):
    method_decorators = [jwt_required]

    def get(self, task_id):
        schema = TaskSchema()
        task = Task.query.get_or_404(task_id)
        return {"task": schema.dump(task)}

    def put(self, task_id):
        schema = TaskSchema(exclude=['done'], partial=True)
        task = Task.query.get_or_404(task_id)
        task = schema.load(request.json, instance=task)
        db.session.commit()
        return {"msg": "task updated", "task": schema.dump(task)}

    def delete(self, task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return {"msg": "task deleted"}

class TaskExecuteResource(Resource):
    method_decorators = [jwt_required]

    def post(self, task_id):
        task = Task.query.get_or_404(task_id)
        task.done = True
        send_email_all_user.delay('Задание {} выполнено. ID: {}'.format(task.title, task.id))
        db.session.commit()
        return {"msg": "task executed"}

