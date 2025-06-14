from datetime import date
from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


class Plan(BaseModel):
    id: UUID
    name: str
    price: float
    payment_term_days: int
    billing_interval: str  # 1M, 3M, 12M


class Invoice(BaseModel):
    id: UUID
    is_paid: bool
    due_date: date
    issue_date: date
    user_id: int
    subscription_id: UUID | None = None
    extra_service_id: UUID | None = None
    # either of the above 2 id's should be null


class ExtraService(BaseModel):
    id: UUID
    name: str
    price: float
    payment_term_days: int


class Subscription(BaseModel):
    # de facto User
    id: UUID
    user_id: int
    plan_id: UUID
    renewal_date: date  # on or after the next invoice issued
    end_date: date  # no renewals after this date
