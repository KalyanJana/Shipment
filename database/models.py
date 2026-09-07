from datetime import datetime
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Column, DateTime, Field, SQLModel


class ShipmentStatus(str, Enum):
    placed= "placed"
    in_transit="in_transit"
    out_for_delivery="out_for_delivery"
    delivered="delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"

    id: int = Field(default=None, primary_key=True)
    content: str
    weight: float = Field(lt=25)
    destination: int
    status: ShipmentStatus
    # Explicitly set timezone=True for PostgreSQL TIMESTAMPTZ
    estimated_delivery: datetime = Field(
        sa_column=Column(DateTime(timezone=True))
    )

class Seller(SQLModel, table=True):
    __tablename__ = "seller"

    id: int = Field(default=None, primary_key=True)
    name:str

    email: EmailStr
    password_hash: str