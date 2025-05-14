from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Enum as SQLEnum, Numeric
from app import db


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True)
    from_account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('accounts.id'), nullable=True
    )
    to_account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('accounts.id'), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        db.String(255), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    from_account = relationship(
        "Account",
        foreign_keys=[from_account_id],
        back_populates="transactions_sent"
    )
    to_account = relationship(
        "Account",
        foreign_keys=[to_account_id],
        back_populates="transactions_received"
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'from_account_id': self.from_account_id,
            'to_account_id': self.to_account_id,
            'amount': str(self.amount),
            'type': self.type.value,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }
