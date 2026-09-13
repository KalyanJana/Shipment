from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from learning.database.models import ShipmentEvent, ShipmentStatus


class BaseShipment(BaseModel):
    content: str = Field(max_length=30)
    weight: float = Field(gt=0, lt=25)
    destination: int


class ShipmentRead(BaseShipment):
    id: UUID
    timeline: list[ShipmentEvent]
    estimated_delivery: datetime
    seller_id: UUID
    delivery_partner_id: UUID | None


class ShipmentCreate(BaseShipment):
    pass


class ShipmentUpdate(BaseModel):
    location: int | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    description: str | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)
