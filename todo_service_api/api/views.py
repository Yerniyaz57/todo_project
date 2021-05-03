from flask import Blueprint, current_app, jsonify
from flask_restful import Api
from marshmallow import ValidationError
from todo_service_api.extensions import apispec
from todo_service_api.api.resources import UserResource, UserList, TaskListResources, TaskResource, TaskExecuteResource
from todo_service_api.api.schemas import UserSchema


blueprint = Blueprint("api", __name__, url_prefix="/api")
api = Api(blueprint)


api.add_resource(UserResource, "/users", endpoint="user_by_id")
api.add_resource(UserList, "/users", endpoint="users")
api.add_resource(TaskListResources, "/todo", endpoint="task_list")
api.add_resource(TaskResource, "/todo/<int:task_id>", endpoint="task_by_id")
api.add_resource(TaskExecuteResource, "/todo/<int:task_id>/execute", endpoint="task_executed")


@blueprint.before_app_first_request
def register_views():
    apispec.spec.components.schema("UserSchema", schema=UserSchema)
    apispec.spec.path(view=UserResource, app=current_app)
    apispec.spec.path(view=UserList, app=current_app)


@blueprint.errorhandler(ValidationError)
def handle_marshmallow_error(e):
    """Return json error for marshmallow validation errors.

    This will avoid having to try/catch ValidationErrors in all endpoints, returning
    correct JSON response with associated HTTP 400 Status (https://tools.ietf.org/html/rfc7231#section-6.5.1)
    """
    return jsonify(e.messages), 400
