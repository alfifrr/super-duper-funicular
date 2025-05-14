import random
import string
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.user import User
from app.models.account import Account, AccountType
from app.schemas.account_schema import AccountCreateSchema, AccountUpdateSchema
from app.utils.response import api_response
from app import db

accounts_bp = Blueprint('accounts', __name__)


def generate_account_number() -> str:
    """Generate a random 12-digit account number."""
    return ''.join(random.choices(string.digits, k=12))


@accounts_bp.route('', methods=['GET'])
@jwt_required()
def get_user_accounts():
    current_user_id = get_jwt_identity()
    accounts = Account.query.filter_by(user_id=current_user_id).all()

    return api_response(
        "Accounts retrieved successfully",
        200,
        data=[account.to_dict() for account in accounts] if accounts else []
    )


@accounts_bp.route('/<int:account_id>', methods=['GET'])
@jwt_required()
def get_account_by_id(account_id: int):
    current_user_id = get_jwt_identity()
    account = Account.query.filter_by(
        id=account_id, user_id=current_user_id).first()

    if not account:
        return api_response(
            "Account not found",
            404,
            errors={
                "message": "The requested account does not exist or you don't have access to it"}
        )

    return api_response(
        "Account retrieved successfully",
        200,
        data=account.to_dict()
    )


@accounts_bp.route('', methods=['POST'])
@jwt_required()
def create_account():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return api_response(
            "User not found",
            404,
            errors={"message": "The requested user does not exist"}
        )

    data = request.get_json()
    account_data = AccountCreateSchema.validate(data)

    if not account_data:
        return api_response(
            "Invalid input data",
            400,
            errors={
                "message": "Invalid or missing account type. Must be either 'checking' or 'savings'"}
        )

    try:
        # Generate a unique account number
        while True:
            account_number = generate_account_number()
            if not Account.query.filter_by(account_number=account_number).first():
                break

        account = Account(
            user_id=current_user_id,
            account_type=AccountType(account_data.account_type),
            account_number=account_number,
            balance=0.00
        )

        db.session.add(account)
        db.session.commit()

        return api_response(
            "Account created successfully",
            201,
            data=account.to_dict()
        )

    except IntegrityError:
        db.session.rollback()
        return api_response(
            "Database integrity error",
            409,
            errors={"message": "Could not create account due to a conflict"}
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return api_response(
            "Database error occurred",
            500,
            errors={"message": "An error occurred while creating the account"}
        )


@accounts_bp.route('/<int:account_id>', methods=['PUT'])
@jwt_required()
def update_account(account_id: int):
    current_user_id = get_jwt_identity()
    account = Account.query.filter_by(
        id=account_id, user_id=current_user_id).first()

    if not account:
        return api_response(
            "Account not found",
            404,
            errors={
                "message": "The requested account does not exist or you don't have access to it"}
        )

    data = request.get_json()
    account_data = AccountUpdateSchema.validate(data)

    if not account_data:
        return api_response(
            "Invalid input data",
            400,
            errors={
                "message": "Invalid or missing account type. Must be either 'checking' or 'savings'"}
        )

    try:
        account.account_type = AccountType(account_data.account_type)
        db.session.commit()

        return api_response(
            "Account updated successfully",
            200,
            data=account.to_dict()
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        return api_response(
            "Database error occurred",
            500,
            errors={"message": "An error occurred while updating the account"}
        )


@accounts_bp.route('/<int:account_id>', methods=['DELETE'])
@jwt_required()
def delete_account(account_id: int):
    current_user_id = get_jwt_identity()
    account = Account.query.filter_by(
        id=account_id, user_id=current_user_id).first()

    if not account:
        return api_response(
            "Account not found",
            404,
            errors={
                "message": "The requested account does not exist or you don't have access to it"}
        )

    try:
        db.session.delete(account)
        db.session.commit()

        return api_response(
            "Account deleted successfully",
            200
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        return api_response(
            "Database error occurred",
            500,
            errors={"message": "An error occurred while deleting the account"}
        )
