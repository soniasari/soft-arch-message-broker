from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Enum, ForeignKey
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