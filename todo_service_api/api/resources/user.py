from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from todo_service_api.api.schemas import UserSchema
from todo_service_api.models import User
from todo_service_api.extensions import db
from todo_service_api.commons.pagination import paginate


class UserResource(Resource):
    method_decorators = [jwt_required]

    def get(self):
        schema = UserSchema()
        user_identity = get_jwt_identity()
        user = User.query.get_or_404(user_identity)
        return {"user": schema.dump(user)}

    def put(self):
        schema = UserSchema(partial=True)
        user_identity = get_jwt_identity()
        user = User.query.get_or_404(user_identity)
        user = schema.load(request.json, instance=user)

        db.session.commit()

        return {"msg": "user updated", "user": schema.dump(user)}


class UserList(Resource):
    def post(self):
        schema = UserSchema()
        user = schema.load(request.json)
        db.session.add(user)
        db.session.commit()
        return {"msg": "user created", "user": schema.dump(user)}, 201
