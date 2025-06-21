from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from typing import Optional
import asyncpg
import os
from dotenv import load_dotenv
from uuid import UUID

from loguru import logger

from repo import Repo
from db_2025.subscriptions.model import User, Plan, Invoice, ExtraService, Subscription

"""
Created with AI via prompt:

create app.py with full api using fastapi library 
and providing access to all CRUD operations from the repo.py

{contents of repo.py}

"""

# Load environment variables
load_dotenv()

# Global repository instance
repo: Optional[Repo] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global repo
    # Startup
    database_url = os.getenv("DB_URL")
    pool = await asyncpg.create_pool(database_url)
    logger.info("database connected!")
    repo = Repo(pool)

    yield

    # Shutdown
    if pool:
        await pool.close()


app = FastAPI(
    title="Subscription Management API",
    description="API for managing users, plans, subscriptions, invoices, and extra services",
    version="1.0.0",
    lifespan=lifespan
)


def get_repo() -> Repo:
    if repo is None:
        raise HTTPException(status_code=500, detail="Repository not initialized")
    return repo


# Define the origins that should be allowed (e.g., your Next.js frontend)
origins = [
    "http://localhost:3000",  # Your Next.js frontend
    # Add more origins if needed, e.g., "http://localhost:8000" for testing
]
# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies or auth headers (if needed)
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# User endpoints
@app.post("/users/", response_model=User, status_code=201)
async def create_user(user: User, repo: Repo = Depends(get_repo)):
    try:
        return await repo.create_user(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, repo: Repo = Depends(get_repo)):
    user = await repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/", response_model=list[User])
async def get_all_users(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        repo: Repo = Depends(get_repo)
):
    return await repo.get_all_users(limit, offset)


@app.get("/users/count/")
async def get_users_count(repo: Repo = Depends(get_repo)):
    count = await repo.get_users_count()
    return {"count": count}


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: User, repo: Repo = Depends(get_repo)):
    user.id = user_id
    updated_user = await repo.update_user(user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@app.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, repo: Repo = Depends(get_repo)):
    success = await repo.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


# Plan endpoints
@app.post("/plans/", response_model=Plan, status_code=201)
async def create_plan(plan: Plan, repo: Repo = Depends(get_repo)):
    try:
        return await repo.create_plan(plan)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/plans/{plan_id}", response_model=Plan)
async def get_plan(plan_id: UUID, repo: Repo = Depends(get_repo)):
    plan = await repo.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@app.get("/plans/", response_model=list[Plan])
async def get_all_plans(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        repo: Repo = Depends(get_repo)
):
    return await repo.get_all_plans(limit, offset)


@app.get("/plans/count/")
async def get_plans_count(repo: Repo = Depends(get_repo)):
    count = await repo.get_plans_count()
    return {"count": count}


@app.put("/plans/{plan_id}", response_model=Plan)
async def update_plan(plan_id: UUID, plan: Plan, repo: Repo = Depends(get_repo)):
    plan.id = plan_id
    updated_plan = await repo.update_plan(plan)
    if not updated_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return updated_plan


@app.delete("/plans/{plan_id}", status_code=204)
async def delete_plan(plan_id: UUID, repo: Repo = Depends(get_repo)):
    success = await repo.delete_plan(plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")


# Invoice endpoints
@app.post("/invoices/", response_model=Invoice, status_code=201)
async def create_invoice(invoice: Invoice, repo: Repo = Depends(get_repo)):
    try:
        return await repo.create_invoice(invoice)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: UUID, repo: Repo = Depends(get_repo)):
    invoice = await repo.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@app.get("/invoices/", response_model=list[Invoice])
async def get_all_invoices(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        repo: Repo = Depends(get_repo)
):
    return await repo.get_all_invoices(limit, offset)


@app.get("/invoices/count/")
async def get_invoices_count(repo: Repo = Depends(get_repo)):
    count = await repo.get_invoices_count()
    return {"count": count}


@app.put("/invoices/{invoice_id}", response_model=Invoice)
async def update_invoice(invoice_id: UUID, invoice: Invoice, repo: Repo = Depends(get_repo)):
    invoice.id = invoice_id
    updated_invoice = await repo.update_invoice(invoice)
    if not updated_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated_invoice


@app.delete("/invoices/{invoice_id}", status_code=204)
async def delete_invoice(invoice_id: UUID, repo: Repo = Depends(get_repo)):
    success = await repo.delete_invoice(invoice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found")


# ExtraService endpoints
@app.post("/extra-services/", response_model=ExtraService, status_code=201)
async def create_extra_service(extra_service: ExtraService, repo: Repo = Depends(get_repo)):
    try:
        return await repo.create_extra_service(extra_service)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/extra-services/{service_id}", response_model=ExtraService)
async def get_extra_service(service_id: UUID, repo: Repo = Depends(get_repo)):
    service = await repo.get_extra_service(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Extra service not found")
    return service


@app.get("/extra-services/", response_model=list[ExtraService])
async def get_all_extra_services(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        repo: Repo = Depends(get_repo)
):
    return await repo.get_all_extra_services(limit, offset)


@app.get("/extra-services/count/")
async def get_extra_services_count(repo: Repo = Depends(get_repo)):
    count = await repo.get_extra_services_count()
    return {"count": count}


@app.put("/extra-services/{service_id}", response_model=ExtraService)
async def update_extra_service(service_id: UUID, extra_service: ExtraService, repo: Repo = Depends(get_repo)):
    extra_service.id = service_id
    updated_service = await repo.update_extra_service(extra_service)
    if not updated_service:
        raise HTTPException(status_code=404, detail="Extra service not found")
    return updated_service


@app.delete("/extra-services/{service_id}", status_code=204)
async def delete_extra_service(service_id: UUID, repo: Repo = Depends(get_repo)):
    success = await repo.delete_extra_service(service_id)
    if not success:
        raise HTTPException(status_code=404, detail="Extra service not found")


# Subscription endpoints
@app.post("/subscriptions/", response_model=Subscription, status_code=201)
async def create_subscription(subscription: Subscription, repo: Repo = Depends(get_repo)):
    try:
        return await repo.create_subscription(subscription)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/subscriptions/{subscription_id}", response_model=Subscription)
async def get_subscription(subscription_id: UUID, repo: Repo = Depends(get_repo)):
    subscription = await repo.get_subscription(subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription


@app.get("/subscriptions/", response_model=list[Subscription])
async def get_all_subscriptions(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        repo: Repo = Depends(get_repo)
):
    return await repo.get_all_subscriptions(limit, offset)


@app.get("/subscriptions/count/")
async def get_subscriptions_count(repo: Repo = Depends(get_repo)):
    count = await repo.get_subscriptions_count()
    return {"count": count}


@app.put("/subscriptions/{subscription_id}", response_model=Subscription)
async def update_subscription(subscription_id: UUID, subscription: Subscription, repo: Repo = Depends(get_repo)):
    subscription.id = subscription_id
    updated_subscription = await repo.update_subscription(subscription)
    if not updated_subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return updated_subscription


@app.delete("/subscriptions/{subscription_id}", status_code=204)
async def delete_subscription(subscription_id: UUID, repo: Repo = Depends(get_repo)):
    success = await repo.delete_subscription(subscription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)