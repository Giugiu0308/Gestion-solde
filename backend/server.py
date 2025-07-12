from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class TransactionType(str, Enum):
    DUE = "due"  # Montant dû
    PAID = "paid"  # Montant payé


class Worker(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkerCreate(BaseModel):
    name: str
    position: Optional[str] = None
    phone: Optional[str] = None


class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    worker_id: str
    type: TransactionType
    amount: float
    description: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)


class TransactionCreate(BaseModel):
    worker_id: str
    type: TransactionType
    amount: float
    description: Optional[str] = None


class WorkerBalance(BaseModel):
    worker: Worker
    total_due: float
    total_paid: float
    balance: float  # total_due - total_paid
    transactions: List[Transaction]


# Worker endpoints
@api_router.post("/workers", response_model=Worker)
async def create_worker(worker_data: WorkerCreate):
    worker = Worker(**worker_data.dict())
    await db.workers.insert_one(worker.dict())
    return worker


@api_router.get("/workers", response_model=List[Worker])
async def get_workers():
    workers = await db.workers.find().to_list(1000)
    return [Worker(**worker) for worker in workers]


@api_router.get("/workers/{worker_id}", response_model=Worker)
async def get_worker(worker_id: str):
    worker = await db.workers.find_one({"id": worker_id})
    if not worker:
        raise HTTPException(status_code=404, detail="Ouvrier non trouvé")
    return Worker(**worker)


# Transaction endpoints
@api_router.post("/transactions", response_model=Transaction)
async def create_transaction(transaction_data: TransactionCreate):
    # Vérifier que l'ouvrier existe
    worker = await db.workers.find_one({"id": transaction_data.worker_id})
    if not worker:
        raise HTTPException(status_code=404, detail="Ouvrier non trouvé")
    
    transaction = Transaction(**transaction_data.dict())
    await db.transactions.insert_one(transaction.dict())
    return transaction


@api_router.get("/transactions", response_model=List[Transaction])
async def get_transactions():
    transactions = await db.transactions.find().sort("date", -1).to_list(1000)
    return [Transaction(**transaction) for transaction in transactions]


@api_router.get("/workers/{worker_id}/transactions", response_model=List[Transaction])
async def get_worker_transactions(worker_id: str):
    transactions = await db.transactions.find({"worker_id": worker_id}).sort("date", -1).to_list(1000)
    return [Transaction(**transaction) for transaction in transactions]


# Balance calculation endpoint
@api_router.get("/workers/{worker_id}/balance", response_model=WorkerBalance)
async def get_worker_balance(worker_id: str):
    # Récupérer l'ouvrier
    worker_data = await db.workers.find_one({"id": worker_id})
    if not worker_data:
        raise HTTPException(status_code=404, detail="Ouvrier non trouvé")
    
    worker = Worker(**worker_data)
    
    # Récupérer toutes les transactions de l'ouvrier
    transactions_data = await db.transactions.find({"worker_id": worker_id}).sort("date", -1).to_list(1000)
    transactions = [Transaction(**t) for t in transactions_data]
    
    # Calculer les totaux
    total_due = sum(t.amount for t in transactions if t.type == TransactionType.DUE)
    total_paid = sum(t.amount for t in transactions if t.type == TransactionType.PAID)
    balance = total_due - total_paid
    
    return WorkerBalance(
        worker=worker,
        total_due=total_due,
        total_paid=total_paid,
        balance=balance,
        transactions=transactions
    )


# Get all workers with their balances
@api_router.get("/workers-balances", response_model=List[WorkerBalance])
async def get_all_workers_balances():
    workers = await db.workers.find().to_list(1000)
    balances = []
    
    for worker_data in workers:
        worker = Worker(**worker_data)
        
        # Récupérer les transactions de chaque ouvrier
        transactions_data = await db.transactions.find({"worker_id": worker.id}).sort("date", -1).to_list(1000)
        transactions = [Transaction(**t) for t in transactions_data]
        
        # Calculer les totaux
        total_due = sum(t.amount for t in transactions if t.type == TransactionType.DUE)
        total_paid = sum(t.amount for t in transactions if t.type == TransactionType.PAID)
        balance = total_due - total_paid
        
        balances.append(WorkerBalance(
            worker=worker,
            total_due=total_due,
            total_paid=total_paid,
            balance=balance,
            transactions=transactions
        ))
    
    return balances


@api_router.delete("/workers/{worker_id}")
async def delete_worker(worker_id: str):
    # Supprimer l'ouvrier
    result = await db.workers.delete_one({"id": worker_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ouvrier non trouvé")
    
    # Supprimer toutes les transactions de cet ouvrier
    await db.transactions.delete_many({"worker_id": worker_id})
    
    return {"message": "Ouvrier et ses transactions supprimés avec succès"}


@api_router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str):
    result = await db.transactions.delete_one({"id": transaction_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction non trouvée")
    
    return {"message": "Transaction supprimée avec succès"}


# Health check
@api_router.get("/")
async def root():
    return {"message": "API de gestion des paies des ouvriers"}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()