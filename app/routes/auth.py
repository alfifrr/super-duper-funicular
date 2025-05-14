from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models.user import User
from app.schemas.user_schema import UserLoginSchema
from app.utils.response import api_response
from app import db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_data = UserLoginSchema.validate(data)

    if not user_data:
        return api_response("Invalid input data", 400, errors={"message": "Missing required fields"})

    user = User.query.filter_by(username=user_data.username).first()

    if not user or not user.check_password(user_data.password):
        return api_response("Invalid credentials", 401)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return api_response(
        "Login successful",
        200,
        data={
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    )
