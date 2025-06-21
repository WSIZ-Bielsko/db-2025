import pytest
import asyncpg
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock
import os
from dotenv import load_dotenv

from repo import Repo
from db_2025.subscriptions.model import User, Plan, Invoice, ExtraService, Subscription

# Load environment variables for database connection
load_dotenv()


@pytest.fixture
async def db_pool():
    """Create a test database connection pool."""
    # You'll need to set up test database credentials in your .env file
    # or use environment variables like TEST_DATABASE_URL
    database_url = os.getenv('TEST_DATABASE_URL', 'postgresql://user:password@localhost/test_db')

    pool = await asyncpg.create_pool(database_url)
    yield pool
    await pool.close()


@pytest.fixture
async def repo(db_pool):
    """Create a repository instance with the test database pool."""
    return Repo(db_pool)


@pytest.fixture
async def clean_db(db_pool):
    """Clean the database before each test."""
    async with db_pool.acquire() as conn:
        # Clean up all tables in reverse order to respect foreign key constraints
        await conn.execute("DELETE FROM invoices")
        await conn.execute("DELETE FROM subscriptions")
        await conn.execute("DELETE FROM extra_services")
        await conn.execute("DELETE FROM plans")
        await conn.execute("DELETE FROM users")


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(name="Test User", id=0)


@pytest.fixture
def sample_plan():
    """Create a sample plan for testing."""
    return Plan(
        name="Basic Plan",
        price=Decimal("19.99"),
        payment_term_days=30,
        billing_interval=30
    )


@pytest.fixture
def sample_extra_service():
    """Create a sample extra service for testing."""
    return ExtraService(
        name="Premium Support",
        price=Decimal("9.99"),
        payment_term_days=7
    )


class TestUserOperations:
    """Test suite for User CRUD operations."""

    async def test_create_user(self, repo, clean_db, sample_user):
        """Test creating a new user."""
        created_user = await repo.create_user(sample_user)

        assert created_user.id is not None
        assert created_user.name == sample_user.name
        assert isinstance(created_user.id, int)

    async def test_get_user(self, repo, clean_db, sample_user):
        """Test retrieving a user by ID."""
        created_user = await repo.create_user(sample_user)
        retrieved_user = await repo.get_user(created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.name == created_user.name

    async def test_get_user_not_found(self, repo, clean_db):
        """Test retrieving a non-existent user."""
        user = await repo.get_user(99999)
        assert user is None

    async def test_get_all_users(self, repo, clean_db):
        """Test retrieving all users with pagination."""
        # Create multiple users
        users = [User(name=f"User {i}") for i in range(5)]
        created_users = []
        for user in users:
            created_user = await repo.create_user(user)
            created_users.append(created_user)

        # Test getting all users
        all_users = await repo.get_all_users(limit=10, offset=0)
        assert len(all_users) == 5

        # Test pagination
        first_page = await repo.get_all_users(limit=2, offset=0)
        assert len(first_page) == 2

        second_page = await repo.get_all_users(limit=2, offset=2)
        assert len(second_page) == 2

    async def test_get_users_count(self, repo, clean_db, sample_user):
        """Test counting users."""
        initial_count = await repo.get_users_count()
        assert initial_count == 0

        await repo.create_user(sample_user)
        count_after_create = await repo.get_users_count()
        assert count_after_create == 1

    async def test_update_user(self, repo, clean_db, sample_user):
        """Test updating a user."""
        created_user = await repo.create_user(sample_user)
        created_user.name = "Updated User"

        updated_user = await repo.update_user(created_user)
        assert updated_user is not None
        assert updated_user.name == "Updated User"
        assert updated_user.id == created_user.id

    async def test_update_user_not_found(self, repo, clean_db):
        """Test updating a non-existent user."""
        user = User(id=99999, name="Non-existent User")
        updated_user = await repo.update_user(user)
        assert updated_user is None

    async def test_delete_user(self, repo, clean_db, sample_user):
        """Test deleting a user."""
        created_user = await repo.create_user(sample_user)

        delete_result = await repo.delete_user(created_user.id)
        assert delete_result is True

        # Verify user is deleted
        retrieved_user = await repo.get_user(created_user.id)
        assert retrieved_user is None

    async def test_delete_user_not_found(self, repo, clean_db):
        """Test deleting a non-existent user."""
        delete_result = await repo.delete_user(99999)
        assert delete_result is False


class TestPlanOperations:
    """Test suite for Plan CRUD operations."""

    async def test_create_plan(self, repo, clean_db, sample_plan):
        """Test creating a new plan."""
        created_plan = await repo.create_plan(sample_plan)

        assert created_plan.id is not None
        assert created_plan.name == sample_plan.name
        assert created_plan.price == sample_plan.price
        assert isinstance(created_plan.id, UUID)

    async def test_get_plan(self, repo, clean_db, sample_plan):
        """Test retrieving a plan by ID."""
        created_plan = await repo.create_plan(sample_plan)
        retrieved_plan = await repo.get_plan(created_plan.id)

        assert retrieved_plan is not None
        assert retrieved_plan.id == created_plan.id
        assert retrieved_plan.name == created_plan.name

    async def test_get_all_plans(self, repo, clean_db):
        """Test retrieving all plans."""
        plans = [
            Plan(name=f"Plan {i}", price=Decimal(f"{i * 10}.99"), payment_term_days=30, billing_interval=30)
            for i in range(3)
        ]

        for plan in plans:
            await repo.create_plan(plan)

        all_plans = await repo.get_all_plans()
        assert len(all_plans) == 3

    async def test_get_plans_count(self, repo, clean_db, sample_plan):
        """Test counting plans."""
        initial_count = await repo.get_plans_count()
        assert initial_count == 0

        await repo.create_plan(sample_plan)
        count_after_create = await repo.get_plans_count()
        assert count_after_create == 1


class TestInvoiceOperations:
    """Test suite for Invoice CRUD operations."""

    async def test_create_invoice_with_subscription(self, repo, clean_db, sample_user, sample_plan):
        """Test creating an invoice linked to a subscription."""
        # Create prerequisites
        created_user = await repo.create_user(sample_user)
        created_plan = await repo.create_plan(sample_plan)

        subscription = Subscription(
            user_id=created_user.id,
            plan_id=created_plan.id,
            renewal_date=date.today(),
            end_date=date.today()
        )
        created_subscription = await repo.create_subscription(subscription)

        # Create invoice
        invoice = Invoice(
            is_paid=False,
            due_date=date.today(),
            issue_date=date.today(),
            user_id=created_user.id,
            subscription_id=created_subscription.id,
            extra_service_id=None
        )

        created_invoice = await repo.create_invoice(invoice)
        assert created_invoice.id is not None
        assert created_invoice.user_id == created_user.id
        assert created_invoice.subscription_id == created_subscription.id

    async def test_get_all_invoices_sorted(self, repo, clean_db, sample_user):
        """Test that invoices are sorted by issue_date DESC."""
        created_user = await repo.create_user(sample_user)

        # Create invoices with different issue dates
        invoice1 = Invoice(
            is_paid=False,
            due_date=date(2023, 1, 15),
            issue_date=date(2023, 1, 1),
            user_id=created_user.id,
            subscription_id=None,
            extra_service_id=None
        )

        invoice2 = Invoice(
            is_paid=False,
            due_date=date(2023, 1, 25),
            issue_date=date(2023, 1, 10),
            user_id=created_user.id,
            subscription_id=None,
            extra_service_id=None
        )

        await repo.create_invoice(invoice1)
        await repo.create_invoice(invoice2)

        all_invoices = await repo.get_all_invoices()
        assert len(all_invoices) == 2
        # Should be sorted by issue_date DESC, so invoice2 should come first
        assert all_invoices[0].issue_date == date(2023, 1, 10)
        assert all_invoices[1].issue_date == date(2023, 1, 1)


class TestExtraServiceOperations:
    """Test suite for ExtraService CRUD operations."""

    async def test_create_extra_service(self, repo, clean_db, sample_extra_service):
        """Test creating a new extra service."""
        created_service = await repo.create_extra_service(sample_extra_service)

        assert created_service.id is not None
        assert created_service.name == sample_extra_service.name
        assert created_service.price == sample_extra_service.price

    async def test_update_extra_service(self, repo, clean_db, sample_extra_service):
        """Test updating an extra service."""
        created_service = await repo.create_extra_service(sample_extra_service)
        created_service.name = "Updated Service"
        created_service.price = Decimal("15.99")

        updated_service = await repo.update_extra_service(created_service)
        assert updated_service is not None
        assert updated_service.name == "Updated Service"
        assert updated_service.price == Decimal("15.99")


class TestSubscriptionOperations:
    """Test suite for Subscription CRUD operations."""

    async def test_create_subscription(self, repo, clean_db, sample_user, sample_plan):
        """Test creating a new subscription."""
        created_user = await repo.create_user(sample_user)
        created_plan = await repo.create_plan(sample_plan)

        subscription = Subscription(
            user_id=created_user.id,
            plan_id=created_plan.id,
            renewal_date=date.today(),
            end_date=date.today()
        )

        created_subscription = await repo.create_subscription(subscription)
        assert created_subscription.id is not None
        assert created_subscription.user_id == created_user.id
        assert created_subscription.plan_id == created_plan.id

    async def test_get_all_subscriptions_sorted(self, repo, clean_db, sample_user, sample_plan):
        """Test that subscriptions are sorted by renewal_date DESC."""
        created_user = await repo.create_user(sample_user)
        created_plan = await repo.create_plan(sample_plan)

        # Create subscriptions with different renewal dates
        sub1 = Subscription(
            user_id=created_user.id,
            plan_id=created_plan.id,
            renewal_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )

        sub2 = Subscription(
            user_id=created_user.id,
            plan_id=created_plan.id,
            renewal_date=date(2023, 6, 1),
            end_date=date(2024, 5, 31)
        )

        await repo.create_subscription(sub1)
        await repo.create_subscription(sub2)

        all_subscriptions = await repo.get_all_subscriptions()
        assert len(all_subscriptions) == 2
        # Should be sorted by renewal_date DESC
        assert all_subscriptions[0].renewal_date == date(2023, 6, 1)
        assert all_subscriptions[1].renewal_date == date(2023, 1, 1)


class TestIntegrationScenarios:
    """Test suite for integration scenarios involving multiple entities."""

    async def test_complete_subscription_workflow(self, repo, clean_db):
        """Test a complete workflow: user -> plan -> subscription -> invoice."""
        # Create user
        user = User(name="Integration Test User")
        created_user = await repo.create_user(user)

        # Create plan
        plan = Plan(
            name="Integration Plan",
            price=Decimal("29.99"),
            payment_term_days=30,
            billing_interval=30
        )
        created_plan = await repo.create_plan(plan)

        # Create subscription
        subscription = Subscription(
            user_id=created_user.id,
            plan_id=created_plan.id,
            renewal_date=date.today(),
            end_date=date.today()
        )
        created_subscription = await repo.create_subscription(subscription)

        # Create invoice for subscription
        invoice = Invoice(
            is_paid=False,
            due_date=date.today(),
            issue_date=date.today(),
            user_id=created_user.id,
            subscription_id=created_subscription.id,
            extra_service_id=None
        )
        created_invoice = await repo.create_invoice(invoice)

        # Verify all entities are created and linked correctly
        assert created_user.id is not None
        assert created_plan.id is not None
        assert created_subscription.id is not None
        assert created_invoice.id is not None

        assert created_subscription.user_id == created_user.id
        assert created_subscription.plan_id == created_plan.id
        assert created_invoice.user_id == created_user.id
        assert created_invoice.subscription_id == created_subscription.id

    async def test_cascade_delete_considerations(self, repo, clean_db, sample_user):
        """Test behavior when deleting entities that might have dependencies."""
        created_user = await repo.create_user(sample_user)

        # Try to delete user (this might fail if there are foreign key constraints)
        # This test documents the expected behavior
        delete_result = await repo.delete_user(created_user.id)
        assert delete_result is True

        # Verify user is deleted
        retrieved_user = await repo.get_user(created_user.id)
        assert retrieved_user is None