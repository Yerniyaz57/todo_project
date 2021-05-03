import datetime
from flask import request, jsonify, Blueprint, current_app as app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
)

from todo_service_api.models import User
from todo_service_api.api.schemas import UserSchema
from todo_service_api.extensions import pwd_context, jwt, apispec, db
from todo_service_api.auth.helpers import revoke_token, is_token_revoked, add_token_to_database
from todo_service_api.tasks.example import send_email


blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@blueprint.route("/login", methods=["POST"])
def login():
    """Authenticate user and return tokens
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not pwd_context.verify(password, user.password):
        return jsonify({"msg": "Bad credentials"}), 400

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    add_token_to_database(access_token, app.config["JWT_IDENTITY_CLAIM"])
    add_token_to_database(refresh_token, app.config["JWT_IDENTITY_CLAIM"])

    ret = {"access_token": access_token, "refresh_token": refresh_token}
    return jsonify(ret), 200


@blueprint.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh():
    """Get an access token from a refresh token
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    ret = {"access_token": access_token}
    add_token_to_database(access_token, app.config["JWT_IDENTITY_CLAIM"])
    return jsonify(ret), 200


@blueprint.route("/revoke_access", methods=["DELETE"])
@jwt_required
def revoke_access_token():
    """Revoke an access token
    """
    jti = get_raw_jwt()["jti"]
    user_identity = get_jwt_identity()
    revoke_token(jti, user_identity)
    return jsonify({"message": "token revoked"}), 200


@blueprint.route("/revoke_refresh", methods=["DELETE"])
@jwt_refresh_token_required
def revoke_refresh_token():
    """Revoke a refresh token, used mainly for logout
    """
    jti = get_raw_jwt()["jti"]
    user_identity = get_jwt_identity()
    revoke_token(jti, user_identity)
    return jsonify({"message": "token revoked"}), 200


@blueprint.route("/password/forget", methods=["POST"])
def forget_password():
    email = request.json.get("email", None)
    user = User.query.filter_by(email=email).first_or_404()
    expires = datetime.timedelta(hours=24)
    reset_token = create_access_token(identity=user.id, expires_delta=expires)
    add_token_to_database(reset_token, app.config["JWT_IDENTITY_CLAIM"])
    user.active = False
    db.session.commit()
    send_email.delay(reset_token, user.email)
    return {'msg': 'sent to email'}


@blueprint.route("/password/reset", methods=["POST"])
@jwt_required
def reset_password():
    password = request.json.get("password", None)
    jti = get_raw_jwt()["jti"]
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    user.password = password
    db.session.commit()
    revoke_token(jti, current_user)
    send_email.delay('Password reset was successful', user.email)
    return {'msg': 'password reset was successful'}


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return User.query.get(identity)


@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


@blueprint.before_app_first_request
def register_views():
    apispec.spec.path(view=login, app=app)
    apispec.spec.path(view=refresh, app=app)
    apispec.spec.path(view=revoke_access_token, app=app)
    apispec.spec.path(view=revoke_refresh_token, app=app)
    apispec.spec.path(view=forget_password, app=app)
    apispec.spec.path(view=reset_password, app=app)
