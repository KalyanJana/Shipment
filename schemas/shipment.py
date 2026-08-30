from datetime import datetime

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

from learning.database.models import ShipmentStatus


class BaseShipment(SQLModel):
    content: str = Field(max_length=30)
    weight: float = Field(gt=0, lt=25)
    destination: int

class Shipment(BaseShipment, table=True):
    __tablename__ = "shipment"
    id: int = Field(default=None, primary_key=True)
    status: ShipmentStatus
    estimated_delivery: datetime

class ShipmentCreate(BaseShipment):
    pass

class ShipmentUpdate(BaseModel):
    content: str | None = Field(default = None)
    weight: float | None = Field(default= 0, le=25)
    destination: int | None = Field(default=0)
    status : ShipmentStatus | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)


