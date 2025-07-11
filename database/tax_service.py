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