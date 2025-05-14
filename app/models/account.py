from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Enum as SQLEnum, Numeric
from app import db


class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"


class Account(db.Model):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(
        SQLEnum(AccountType), nullable=False
    )
    account_number: Mapped[str] = mapped_column(
        db.String(20), unique=True, nullable=False
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=0.00
    )

    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions_sent = relationship(
        "Transaction",
        foreign_keys="Transaction.from_account_id",
        back_populates="from_account",
        cascade="all, delete-orphan"
    )
    transactions_received = relationship(
        "Transaction",
        foreign_keys="Transaction.to_account_id",
        back_populates="to_account",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_type': self.account_type.value,
            'account_number': self.account_number,
            'balance': str(self.balance),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
