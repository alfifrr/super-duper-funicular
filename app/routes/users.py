from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.user import User
from app.schemas.user_schema import UserSignupSchema, UserUpdateSchema
from app.utils.response import api_response
from app import db

users_bp = Blueprint('users', __name__)


@users_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return api_response(
            "User not found",
            404,
            errors={"message": "The requested user does not exist"}
        )

    return api_response(
        "User profile retrieved successfully",
        200,
        data=user.to_dict()
    )


@users_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return api_response(
            "User not found",
            404,
            errors={"message": "The requested user does not exist"}
        )

    data = request.get_json()
    if 'username' in data:
        return api_response(
            "Username cannot be changed",
            400,
            errors={"message": "Username field cannot be modified"}
        )

    user_data = UserUpdateSchema.validate(data)

    try:
        if user_data.email and user_data.email != user.email:
            if User.query.filter_by(email=user_data.email).first():
                return api_response("Email already exists", 409)
            user.email = user_data.email

        if user_data.password:
            user.set_password(user_data.password)

        db.session.commit()

        return api_response(
            "User updated successfully",
            200,
            data=user.to_dict()
        )

    except IntegrityError:
        db.session.rollback()
        return api_response(
            "Database integrity error",
            409,
            errors={"message": "Email address is already in use"}
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return api_response(
            "Database error occurred",
            500,
            errors={"message": "An error occurred while updating the user"}
        )


@users_bp.route('', methods=['POST'])
def create_user():
    data = request.get_json()
    user_data = UserSignupSchema.validate(data)

    if not user_data:
        return api_response("Invalid input data", 400, errors={"message": "Missing required fields"})

    if User.query.filter_by(username=user_data.username).first():
        return api_response("Username already exists", 409)

    if User.query.filter_by(email=user_data.email).first():
        return api_response("Email already exists", 409)

    try:
        user = User(
            username=user_data.username,
            email=user_data.email
        )
        user.set_password(user_data.password)

        db.session.add(user)
        db.session.commit()

        return api_response(
            "User created successfully",
            201,
            data=user.to_dict()
        )

    except IntegrityError:
        db.session.rollback()
        return api_response(
            "Database integrity error",
            409,
            errors={"message": "Username or email address is already in use"}
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return api_response(
            "Database error occurred",
            500,
            errors={"message": "An error occurred while creating the user"}
        )
