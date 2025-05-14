from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from app.models.account import Account
from app.models import Transaction, TransactionType
from app.schemas import (
    TransactionDepositSchema,
    TransactionTransferSchema,
    TransactionWithdrawalSchema,
    TransactionFilterSchema
)
from app.utils.response import api_response
from app import db

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    current_user_id = get_jwt_identity()

    # Get user's accounts
    user_accounts = Account.query.filter_by(user_id=current_user_id).all()
    if not user_accounts:
        return api_response(
            "Transactions retrieved successfully",
            200,
            data=[]
        )

    account_ids = [account.id for account in user_accounts]

    # Build base query for transactions related to user's accounts
    query = Transaction.query.filter(
        or_(
            Transaction.from_account_id.in_(account_ids),
            Transaction.to_account_id.in_(account_ids)
        )
    )

    # Apply filters if provided
    filter_data = TransactionFilterSchema.validate(request.args)

    if filter_data.account_id:
        if filter_data.account_id not in account_ids:
            return api_response(
                "Account not found",
                404,
                errors={
                    "message": "The specified account does not exist or you don't have access to it"}
            )
        query = query.filter(
            or_(
                Transaction.from_account_id == filter_data.account_id,
                Transaction.to_account_id == filter_data.account_id
            )
        )

    if filter_data.start_date:
        query = query.filter(Transaction.created_at >= filter_data.start_date)

    if filter_data.end_date:
        query = query.filter(Transaction.created_at <= filter_data.end_date)

    # Order by most recent first
    query = query.order_by(Transaction.created_at.desc())

    try:
        transactions = query.all()
        return api_response(
            "Transactions retrieved successfully",
            200,
            data=[transaction.to_dict() for transaction in transactions]
        )
    except SQLAlchemyError as e:
        return api_response(
            "Database error occurred",
            500,
            errors={"message": "An error occurred while retrieving transactions"}
        )


@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id: int):
    current_user_id = get_jwt_identity()

    # Get user's accounts
    user_accounts = Account.query.filter_by(user_id=current_user_id).all()
    if not user_accounts:
        return api_response(
            "Transaction not found",
            404,
            errors={
                "message": "The specified transaction does not exist or you don't have access to it"}
        )

    account_ids = [account.id for account in user_accounts]

    # Find transaction that involves user's accounts
    transaction = Transaction.query.filter(
        Transaction.id == transaction_id,
        or_(
            Transaction.from_account_id.in_(account_ids),
            Transaction.to_account_id.in_(account_ids)
        )
    ).first()

    if not transaction:
        return api_response(
            "Transaction not found",
            404,
            errors={
                "message": "The specified transaction does not exist or you don't have access to it"}
        )

    return api_response(
        "Transaction retrieved successfully",
        200,
        data=transaction.to_dict()
    )


@transactions_bp.route('', methods=['POST'])
@jwt_required()
def create_transaction():
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if 'type' not in data:
        return api_response(
            "Invalid input data",
            400,
            errors={"message": "Transaction type is required"}
        )

    # Validate account ownership and existence
    if 'account_id' not in data:
        return api_response(
            "Invalid input data",
            400,
            errors={"message": "account_id is required"}
        )

    from_account = Account.query.filter_by(
        id=data['account_id'],
        user_id=current_user_id
    ).first()

    if not from_account:
        return api_response(
            "Account not found",
            404,
            errors={
                "message": "The specified account does not exist or you don't have access to it"}
        )

    transaction_type = data.get('type').lower()

    try:
        if transaction_type == TransactionType.DEPOSIT.value:
            return handle_deposit(data, from_account)
        elif transaction_type == TransactionType.WITHDRAWAL.value:
            return handle_withdrawal(data, from_account)
        elif transaction_type == TransactionType.TRANSFER.value:
            return handle_transfer(data, from_account)
        else:
            return api_response(
                "Invalid transaction type",
                400,
                errors={
                    "message": "Transaction type must be 'deposit', 'withdrawal', or 'transfer'"}
            )

    except SQLAlchemyError as e:
        db.session.rollback()
        return api_response(
            "Database error occurred",
            500,
            errors={"message": "An error occurred while processing the transaction"}
        )


def handle_deposit(data: dict, to_account: Account):
    transaction_data = TransactionDepositSchema.validate(data)
    if not transaction_data:
        return api_response(
            "Invalid input data",
            400,
            errors={"message": "Invalid or missing amount. Amount must be positive."}
        )

    transaction = Transaction(
        to_account_id=to_account.id,
        amount=transaction_data.amount,
        type=TransactionType.DEPOSIT,
        description=transaction_data.description
    )

    # Update account balance
    to_account.balance += transaction_data.amount

    db.session.add(transaction)
    db.session.commit()

    return api_response(
        "Transaction created successfully",
        201,
        data={
            "transaction": transaction.to_dict(),
            "account": to_account.to_dict()
        }
    )


def handle_withdrawal(data: dict, from_account: Account):
    transaction_data = TransactionWithdrawalSchema.validate(data)
    if not transaction_data:
        return api_response(
            "Invalid input data",
            400,
            errors={"message": "Invalid or missing amount. Amount must be positive."}
        )

    # Check if account has sufficient funds
    if from_account.balance < transaction_data.amount:
        return api_response(
            "Insufficient funds",
            400,
            errors={
                "message": "Your account balance is insufficient for this withdrawal"}
        )

    transaction = Transaction(
        from_account_id=from_account.id,
        amount=transaction_data.amount,
        type=TransactionType.WITHDRAWAL,
        description=transaction_data.description
    )

    # Update account balance
    from_account.balance -= transaction_data.amount

    db.session.add(transaction)
    db.session.commit()

    return api_response(
        "Transaction created successfully",
        201,
        data={
            "transaction": transaction.to_dict(),
            "account": from_account.to_dict()
        }
    )


def handle_transfer(data: dict, from_account: Account):
    transaction_data = TransactionTransferSchema.validate(data)
    if not transaction_data:
        return api_response(
            "Invalid input data",
            400,
            errors={
                "message": "Invalid or missing fields. Required: amount (positive) and to_account_id"}
        )

    # Check if sender has sufficient funds
    if from_account.balance < transaction_data.amount:
        return api_response(
            "Insufficient funds",
            400,
            errors={
                "message": "Your account balance is insufficient for this transfer"}
        )

    # Validate receiver account exists
    to_account = Account.query.get(transaction_data.to_account_id)
    if not to_account:
        return api_response(
            "Receiver account not found",
            404,
            errors={"message": "The recipient account does not exist"}
        )

    # Prevent transfer to same account
    if from_account.id == to_account.id:
        return api_response(
            "Invalid transfer",
            400,
            errors={"message": "Cannot transfer to the same account"}
        )

    transaction = Transaction(
        from_account_id=from_account.id,
        to_account_id=to_account.id,
        amount=transaction_data.amount,
        type=TransactionType.TRANSFER,
        description=transaction_data.description
    )

    # Update account balances
    from_account.balance -= transaction_data.amount
    to_account.balance += transaction_data.amount

    db.session.add(transaction)
    db.session.commit()

    return api_response(
        "Transaction created successfully",
        201,
        data={
            "transaction": transaction.to_dict(),
            "from_account": from_account.to_dict(),
            "to_account": to_account.to_dict()
        }
    )
