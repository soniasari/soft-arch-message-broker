# Vehicle Tax Payment API - Complete Project Setup

## 1. Project Setup with UV and FastAPI

### Step 1: Install UV (if not already installed)
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2: Create the project
```bash
# Create project directory
mkdir vehicle-tax-api
cd vehicle-tax-api

# Initialize UV project
uv init

# Add dependencies
uv add fastapi "uvicorn[standard]" mysql-connector-python pydantic sqlalchemy pymysql python-dotenv cryptography

# Add development dependencies
uv add --dev pytest httpx
```

### Step 3: Project structure
```
vehicle-tax-api/
├── pyproject.toml
├── .env
├── main.py
├── database/
│   ├── __init__.py
│   ├── connection.py
│   └── models.py
├── api/
│   ├── __init__.py
│   └── routes.py
├── services/
│   ├── __init__.py
│   └── tax_service.py
└── tests/
    └── __init__.py
```

## 2. Database Script (MySQL)

### Create database and tables
```sql
-- Create database
CREATE DATABASE IF NOT EXISTS vehicle_tax_db;
USE vehicle_tax_db;

-- Create states table
CREATE TABLE states (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    tax_rate DECIMAL(5,4) NOT NULL DEFAULT 0.05,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vehicles table
CREATE TABLE vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plate VARCHAR(20) NOT NULL,
    state_id INT NOT NULL,
    vehicle_type ENUM('car', 'truck', 'motorcycle', 'bus') NOT NULL,
    year INT NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    owner_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES states(id),
    UNIQUE KEY unique_plate_state (plate, state_id)
);

-- Create tax_payments table
CREATE TABLE tax_payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    payment_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    tax_year INT NOT NULL,
    payment_method ENUM('cash', 'credit_card', 'bank_transfer', 'check') NOT NULL,
    transaction_id VARCHAR(100) UNIQUE,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
    UNIQUE KEY unique_vehicle_tax_year (vehicle_id, tax_year)
);
```

## 3. Sample Data Inserts

```sql
-- Insert states
INSERT INTO states (name, code, tax_rate) VALUES
('California', 'CA', 0.0725),
('Texas', 'TX', 0.0625),
('New York', 'NY', 0.08),
('Florida', 'FL', 0.06),
('Illinois', 'IL', 0.0625);

-- Insert vehicles
INSERT INTO vehicles (plate, state_id, vehicle_type, year, value, owner_name) VALUES
('ABC123', 1, 'car', 2020, 25000.00, 'John Doe'),
('XYZ789', 1, 'truck', 2019, 45000.00, 'Jane Smith'),
('DEF456', 2, 'car', 2021, 30000.00, 'Bob Johnson'),
('GHI789', 2, 'motorcycle', 2022, 15000.00, 'Alice Brown'),
('JKL012', 3, 'car', 2018, 20000.00, 'Charlie Wilson'),
('MNO345', 3, 'bus', 2017, 80000.00, 'Transit Co'),
('PQR678', 4, 'car', 2023, 35000.00, 'David Lee'),
('STU901', 5, 'truck', 2020, 50000.00, 'Emma Davis');

-- Insert tax payments
INSERT INTO tax_payments (vehicle_id, payment_date, amount, tax_year, payment_method, transaction_id, status) VALUES
(1, '2024-01-15', 1812.50, 2024, 'credit_card', 'TXN001', 'completed'),
(2, '2024-02-20', 2812.50, 2024, 'bank_transfer', 'TXN002', 'completed'),
(3, '2024-01-10', 1875.00, 2024, 'cash', 'TXN003', 'completed'),
(4, '2024-03-05', 937.50, 2024, 'credit_card', 'TXN004', 'completed'),
(5, '2024-01-25', 1600.00, 2024, 'check', 'TXN005', 'completed'),
(1, '2023-01-15', 1812.50, 2023, 'credit_card', 'TXN006', 'completed'),
(3, '2023-02-10', 1875.00, 2023, 'bank_transfer', 'TXN007', 'completed');
```

## 4. Python Code Implementation

### .env file
```
DATABASE_URL=mysql+pymysql://root:123456@localhost:3306/vehicle_tax_db
```

### database/connection.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### database/models.py
```python
from sqlalchemy import Column, Integer, String, Decimal, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base
import enum

class VehicleType(enum.Enum):
    car = "car"
    truck = "truck"
    motorcycle = "motorcycle"
    bus = "bus"

class PaymentMethod(enum.Enum):
    cash = "cash"
    credit_card = "credit_card"
    bank_transfer = "bank_transfer"
    check = "check"

class PaymentStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class State(Base):
    __tablename__ = "states"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    tax_rate = Column(Numeric(5,4), nullable=False, default=0.05)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    vehicles = relationship("Vehicle", back_populates="state")

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String(20), nullable=False)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    year = Column(Integer, nullable=False)
    value = Column(Numeric(10,2), nullable=False)
    owner_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    state = relationship("State", back_populates="vehicles")
    tax_payments = relationship("TaxPayment", back_populates="vehicle")

class TaxPayment(Base):
    __tablename__ = "tax_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    payment_date = Column(Date, nullable=False)
    amount = Column(Numeric(10,2), nullable=False)
    tax_year = Column(Integer, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    transaction_id = Column(String(100), unique=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    vehicle = relationship("Vehicle", back_populates="tax_payments")
```

### services/tax_service.py
```python
from sqlalchemy.orm import Session
from database.models import Vehicle, TaxPayment, State
from decimal import Decimal
import uuid
from datetime import date

class TaxService:
    
    @staticmethod
    def calculate_tax(vehicle_value: Decimal, tax_rate: Decimal) -> Decimal:
        return vehicle_value * tax_rate
    
    @staticmethod
    def process_payment(
        db: Session,
        plate: str,
        state_code: str,
        tax_year: int,
        payment_method: str
    ) -> dict:
        # Find vehicle
        vehicle = db.query(Vehicle).join(State).filter(
            Vehicle.plate == plate,
            State.code == state_code
        ).first()
        
        if not vehicle:
            return {"error": "Vehicle not found"}
        
        # Check if payment already exists
        existing_payment = db.query(TaxPayment).filter(
            TaxPayment.vehicle_id == vehicle.id,
            TaxPayment.tax_year == tax_year
        ).first()
        
        if existing_payment:
            return {"error": "Payment already exists for this year"}
        
        # Calculate tax amount
        tax_amount = TaxService.calculate_tax(vehicle.value, vehicle.state.tax_rate)
        
        # Create payment
        payment = TaxPayment(
            vehicle_id=vehicle.id,
            payment_date=date.today(),
            amount=tax_amount,
            tax_year=tax_year,
            payment_method=payment_method,
            transaction_id=str(uuid.uuid4()),
            status="completed"
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return {
            "payment_id": payment.id,
            "transaction_id": payment.transaction_id,
            "amount": float(payment.amount),
            "tax_year": payment.tax_year,
            "payment_date": payment.payment_date.isoformat(),
            "status": payment.status.value
        }
    
    @staticmethod
    def get_payments_by_plate_and_state(
        db: Session,
        plate: str,
        state_code: str
    ) -> list:
        payments = db.query(TaxPayment).join(Vehicle).join(State).filter(
            Vehicle.plate == plate,
            State.code == state_code
        ).all()
        
        return [
            {
                "payment_id": payment.id,
                "transaction_id": payment.transaction_id,
                "amount": float(payment.amount),
                "tax_year": payment.tax_year,
                "payment_date": payment.payment_date.isoformat(),
                "payment_method": payment.payment_method.value,
                "status": payment.status.value,
                "vehicle": {
                    "plate": payment.vehicle.plate,
                    "type": payment.vehicle.vehicle_type.value,
                    "year": payment.vehicle.year,
                    "owner": payment.vehicle.owner_name
                }
            }
            for payment in payments
        ]
```

### api/routes.py
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.tax_service import TaxService
from pydantic import BaseModel
from typing import List

router = APIRouter()

class PaymentRequest(BaseModel):
    plate: str
    state_code: str
    tax_year: int
    payment_method: str

class PaymentResponse(BaseModel):
    payment_id: int
    transaction_id: str
    amount: float
    tax_year: int
    payment_date: str
    status: str

class PaymentHistoryResponse(BaseModel):
    payment_id: int
    transaction_id: str
    amount: float
    tax_year: int
    payment_date: str
    payment_method: str
    status: str
    vehicle: dict

@router.post("/payments/", response_model=PaymentResponse)
def create_payment(
    payment_request: PaymentRequest,
    db: Session = Depends(get_db)
):
    result = TaxService.process_payment(
        db=db,
        plate=payment_request.plate,
        state_code=payment_request.state_code,
        tax_year=payment_request.tax_year,
        payment_method=payment_request.payment_method
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/payments/{plate}/{state_code}", response_model=List[PaymentHistoryResponse])
def get_payments(
    plate: str,
    state_code: str,
    db: Session = Depends(get_db)
):
    payments = TaxService.get_payments_by_plate_and_state(
        db=db,
        plate=plate,
        state_code=state_code
    )
    
    if not payments:
        raise HTTPException(status_code=404, detail="No payments found")
    
    return payments

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "Vehicle Tax Payment API"}
```

### main.py
```python
from fastapi import FastAPI
from api.routes import router
from database.connection import engine
from database.models import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vehicle Tax Payment API",
    description="API for simulating vehicle tax payments",
    version="1.0.0"
)

app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 5. Running the Application

```bash
# Start the application
uv run main.py

# Or with uvicorn directly
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 6. HTTP Request Examples (.http format)

### Create a new payment
```http
POST http://localhost:8000/api/v1/payments/
Content-Type: application/json

{
    "plate": "ABC123",
    "state_code": "CA",
    "tax_year": 2024,
    "payment_method": "credit_card"
}
```

### Get payment history by plate and state
```http
GET http://localhost:8000/api/v1/payments/ABC123/CA
```

### Get payments for a different vehicle
```http
GET http://localhost:8000/api/v1/payments/DEF456/TX
```

### Create payment for motorcycle
```http
POST http://localhost:8000/api/v1/payments/
Content-Type: application/json

{
    "plate": "GHI789",
    "state_code": "TX",
    "tax_year": 2024,
    "payment_method": "bank_transfer"
}
```

### Health check
```http
GET http://localhost:8000/api/v1/health
```

### Try to create duplicate payment (should fail)
```http
POST http://localhost:8000/api/v1/payments/
Content-Type: application/json

{
    "plate": "ABC123",
    "state_code": "CA",
    "tax_year": 2024,
    "payment_method": "cash"
}
```

### Get payments for non-existent vehicle (should return 404)
```http
GET http://localhost:8000/api/v1/payments/NONEXISTENT/CA
```

## 7. Testing the Setup

1. Make sure MySQL is running on localhost:3306
2. Create the database and tables using the SQL scripts
3. Insert the sample data
4. Run the Python application
5. Use the HTTP requests to test the endpoints

The API will be available at `http://localhost:8000` and the interactive documentation at `http://localhost:8000/docs`.
