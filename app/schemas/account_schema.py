from dataclasses import dataclass
from typing import Optional
from app.models.account import AccountType


@dataclass
class AccountCreateSchema:
    account_type: str

    @classmethod
    def validate(cls, data: dict) -> Optional['AccountCreateSchema']:
        if not data.get('account_type'):
            return None

        account_type = data['account_type'].lower()
        if account_type not in [at.value for at in AccountType]:
            return None

        return cls(account_type=account_type)


@dataclass
class AccountUpdateSchema:
    account_type: str

    @classmethod
    def validate(cls, data: dict) -> Optional['AccountUpdateSchema']:
        if not data.get('account_type'):
            return None

        account_type = data['account_type'].lower()
        if account_type not in [at.value for at in AccountType]:
            return None

        return cls(account_type=account_type)
