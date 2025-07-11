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