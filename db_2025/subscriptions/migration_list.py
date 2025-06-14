from db_2025.u2.migrations.model import Migration


"""
Migration generated via prompt: 

Create SQL to create the database structure for the set of (pydantic) data classess attached below.

- For strings use text fields (not varchar).
- This is latest postgres database .
- Suggest indices where appropriate.
- All monetary columns should hold at most 2 decimals,
- All foreign keys should cascade on delete,
- for UUID primary keys create default (random UUID's) via gen_random_uuid()

{insert model.py here}

"""


migrations = [
    Migration(
        start_version=1,
        produces_version=2,
        description='create initial tables',
        up_sql="""CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    payment_term_days INT NOT NULL,
    billing_interval TEXT NOT NULL
);

CREATE TABLE extra_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    payment_term_days INT NOT NULL
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INT NOT NULL,
    plan_id UUID NOT NULL,
    renewal_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_plan FOREIGN KEY(plan_id) REFERENCES plans(id) ON DELETE CASCADE
);

CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    is_paid BOOLEAN NOT NULL,
    due_date DATE NOT NULL,
    issue_date DATE NOT NULL,
    user_id INT NOT NULL,
    subscription_id UUID NULL,
    extra_service_id UUID NULL,
    CONSTRAINT fk_user_invoice FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_subscription FOREIGN KEY(subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE,
    CONSTRAINT fk_extra_service FOREIGN KEY(extra_service_id) REFERENCES extra_services(id) ON DELETE CASCADE,
    CONSTRAINT check_subscription_or_extra_service CHECK (
        (subscription_id IS NULL AND extra_service_id IS NOT NULL) OR
        (subscription_id IS NOT NULL AND extra_service_id IS NULL)
    )
);
            
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_plan_id ON subscriptions(plan_id);
CREATE INDEX idx_invoices_user_id ON invoices(user_id);
CREATE INDEX idx_invoices_subscription_id ON invoices(subscription_id);
CREATE INDEX idx_invoices_extra_service_id ON invoices(extra_service_id);

 """,
        down_sql=""" 
-- Drop tables in reverse order of creation to respect foreign key constraints
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS extra_services;
DROP TABLE IF EXISTS plans;
DROP TABLE IF EXISTS users;        
        
        
        
        """,
    ),


]

