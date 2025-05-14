from dataclasses import dataclass
from typing import Optional
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone
from app.models import TransactionType


@dataclass
class TransactionDepositSchema:
    amount: Decimal
    description: Optional[str] = None

    @classmethod
    def validate(cls, data: dict) -> Optional['TransactionDepositSchema']:
        if not data.get('amount'):
            return None

        try:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                return None
        except (ValueError, TypeError, InvalidOperation):
            return None

        return cls(
            amount=amount,
            description=data.get('description')
        )


@dataclass
class TransactionWithdrawalSchema:
    amount: Decimal
    description: Optional[str] = None

    @classmethod
    def validate(cls, data: dict) -> Optional['TransactionWithdrawalSchema']:
        if not data.get('amount'):
            return None

        try:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                return None
        except (ValueError, TypeError, InvalidOperation):
            return None

        return cls(
            amount=amount,
            description=data.get('description')
        )


@dataclass
class TransactionTransferSchema:
    amount: Decimal
    to_account_id: int
    description: Optional[str] = None

    @classmethod
    def validate(cls, data: dict) -> Optional['TransactionTransferSchema']:
        if not data.get('amount') or not data.get('to_account_id'):
            return None

        try:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                return None
            to_account_id = int(data['to_account_id'])
        except (ValueError, TypeError, InvalidOperation):
            return None

        return cls(
            amount=amount,
            to_account_id=to_account_id,
            description=data.get('description')
        )


@dataclass
class TransactionFilterSchema:
    account_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @classmethod
    def validate(cls, data: dict) -> 'TransactionFilterSchema':
        filter_data = {}

        # Parse account_id if provided
        if account_id := data.get('account_id'):
            try:
                filter_data['account_id'] = int(account_id)
            except (ValueError, TypeError):
                pass

        # Parse dates if provided, expecting ISO format
        if start_date := data.get('start_date'):
            try:
                filter_data['start_date'] = datetime.fromisoformat(
                    start_date).replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                pass

        if end_date := data.get('end_date'):
            try:
                filter_data['end_date'] = datetime.fromisoformat(
                    end_date).replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                pass

        return cls(**filter_data)
