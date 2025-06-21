from asyncio import run

import asyncpg
from dotenv import load_dotenv

from db_2025.subscriptions.model import *

"""
AI generated repository, using prompt:

Using pydantic 2, and asyncpg (python, postgres database) create repository class, taking pool in constructor arg,
and allowing for full CRUD operations on all relevant tables (which are just plurals of the class name);
relevant functions must return full objects,
and in the read operations select's should use * and not list columns; use python 3.12 
(and avoid importing from typing package, such as using Optional).
In the "get_all" method allow for pagination, while sorting by the natural parameters for each of the classes;
all id's in create operations should be created by the database. For all tables, create also
a count method, returning the number of rows in the table.

"""

class Repo:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    # User CRUD
    async def create_user(self, user: User) -> User:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO users (name) VALUES ($1) RETURNING *",
                user.name
            )
            return User(**row)

    async def get_user(self, id: int) -> User | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", id)
            return User(**row) if row else None

    async def get_all_users(self, limit: int = 10, offset: int = 0) -> list[User]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM users ORDER BY name LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [User(**row) for row in rows]

    async def get_users_count(self) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM users")

    async def update_user(self, user: User) -> User | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE users SET name = $1 WHERE id = $2 RETURNING *",
                user.name, user.id
            )
            return User(**row) if row else None

    async def delete_user(self, id: int) -> bool:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "DELETE FROM users WHERE id = $1 RETURNING id",
                id
            )
            return bool(row)

    # Plan CRUD
    async def create_plan(self, plan: Plan) -> Plan:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO plans (name, price, payment_term_days, billing_interval) VALUES ($1, $2, $3, $4) RETURNING *",
                plan.name, plan.price, plan.payment_term_days, plan.billing_interval
            )
            return Plan(**row)

    async def get_plan(self, id: UUID) -> Plan | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM plans WHERE id = $1", id)
            return Plan(**row) if row else None

    async def get_all_plans(self, limit: int = 10, offset: int = 0) -> list[Plan]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM plans ORDER BY name LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [Plan(**row) for row in rows]

    async def get_plans_count(self) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM plans")

    async def update_plan(self, plan: Plan) -> Plan | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE plans SET name = $1, price = $2, payment_term_days = $3, billing_interval = $4 WHERE id = $5 RETURNING *",
                plan.name, plan.price, plan.payment_term_days, plan.billing_interval, plan.id
            )
            return Plan(**row) if row else None

    async def delete_plan(self, id: UUID) -> bool:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "DELETE FROM plans WHERE id = $1 RETURNING id",
                id
            )
            return bool(row)

    # Invoice CRUD
    async def create_invoice(self, invoice: Invoice) -> Invoice:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO invoices (is_paid, due_date, issue_date, user_id, subscription_id, extra_service_id) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
                invoice.is_paid, invoice.due_date, invoice.issue_date, invoice.user_id,
                invoice.subscription_id, invoice.extra_service_id
            )
            return Invoice(**row)

    async def get_invoice(self, id: UUID) -> Invoice | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM invoices WHERE id = $1", id)
            return Invoice(**row) if row else None

    async def get_all_invoices(self, limit: int = 10, offset: int = 0) -> list[Invoice]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM invoices ORDER BY issue_date DESC LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [Invoice(**row) for row in rows]

    async def get_invoices_count(self) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM invoices")

    async def update_invoice(self, invoice: Invoice) -> Invoice | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE invoices SET is_paid = $1, due_date = $2, issue_date = $3, user_id = $4, subscription_id = $5, extra_service_id = $6 WHERE id = $7 RETURNING *",
                invoice.is_paid, invoice.due_date, invoice.issue_date, invoice.user_id,
                invoice.subscription_id, invoice.extra_service_id, invoice.id
            )
            return Invoice(**row) if row else None

    async def delete_invoice(self, id: UUID) -> bool:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "DELETE FROM invoices WHERE id = $1 RETURNING id",
                id
            )
            return bool(row)

    # ExtraService CRUD
    async def create_extra_service(self, extra_service: ExtraService) -> ExtraService:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO extra_services (name, price, payment_term_days) VALUES ($1, $2, $3) RETURNING *",
                extra_service.name, extra_service.price, extra_service.payment_term_days
            )
            return ExtraService(**row)

    async def get_extra_service(self, id: UUID) -> ExtraService | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM extra_services WHERE id = $1", id)
            return ExtraService(**row) if row else None

    async def get_all_extra_services(self, limit: int = 10, offset: int = 0) -> list[ExtraService]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM extra_services ORDER BY name LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [ExtraService(**row) for row in rows]

    async def get_extra_services_count(self) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM extra_services")

    async def update_extra_service(self, extra_service: ExtraService) -> ExtraService | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE extra_services SET name = $1, price = $2, payment_term_days = $3 WHERE id = $4 RETURNING *",
                extra_service.name, extra_service.price, extra_service.payment_term_days, extra_service.id
            )
            return ExtraService(**row) if row else None

    async def delete_extra_service(self, id: UUID) -> bool:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "DELETE FROM extra_services WHERE id = $1 RETURNING id",
                id
            )
            return bool(row)

    # Subscription CRUD
    async def create_subscription(self, subscription: Subscription) -> Subscription:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "INSERT INTO subscriptions (user_id, plan_id, renewal_date, end_date) VALUES ($1, $2, $3, $4) RETURNING *",
                subscription.user_id, subscription.plan_id, subscription.renewal_date, subscription.end_date
            )
            return Subscription(**row)

    async def get_subscription(self, id: UUID) -> Subscription | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM subscriptions WHERE id = $1", id)
            return Subscription(**row) if row else None

    async def get_all_subscriptions(self, limit: int = 10, offset: int = 0) -> list[Subscription]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM subscriptions ORDER BY renewal_date DESC LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [Subscription(**row) for row in rows]

    async def get_subscriptions_count(self) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM subscriptions")

    async def update_subscription(self, subscription: Subscription) -> Subscription | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE subscriptions SET user_id = $1, plan_id = $2, renewal_date = $3, end_date = $4 WHERE id = $5 RETURNING *",
                subscription.user_id, subscription.plan_id, subscription.renewal_date, subscription.end_date, subscription.id
            )
            return Subscription(**row) if row else None

    async def delete_subscription(self, id: UUID) -> bool:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "DELETE FROM subscriptions WHERE id = $1 RETURNING id",
                id
            )
            return bool(row)


async def main():
    load_dotenv()
    # ... napisac kod testujacy

if __name__ == '__main__':
    run(main())