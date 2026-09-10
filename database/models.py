from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import ARRAY, INTEGER, Column, func
from sqlalchemy.dialects import postgresql
from sqlmodel import DateTime, Field, Relationship, SQLModel


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class User(SQLModel):
    name: str
    email: EmailStr
    password_hash: str

class Seller(User, table=True):
    __tablename__ = "seller"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            postgresql.UUID(as_uuid=True),
            primary_key=True
        )
    )

    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            server_default=func.now()
        )
    )

    shipments: list["Shipment"] = Relationship(
        back_populates="seller"
    )


class DeliveryPartner(User, table=True):
    __tablename__ = "delivery_partner"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            postgresql.UUID(as_uuid=True),
            primary_key=True
        )
    )

    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            server_default=func.now()
        )
    )

    serviceable_zip_codes: list[int] = Field(
        sa_column=Column(ARRAY(INTEGER()))
    )

    max_handling_capacity: int

    shipments: list["Shipment"] = Relationship(
        back_populates="delivery_partner"
    )

    @property
    def active_shipments(self) -> list["Shipment"]:
        return [
            shipment
            for shipment in self.shipments
            if shipment.status != ShipmentStatus.delivered
        ]

    @property
    def current_handling_capacity(self) -> int:
        return self.max_handling_capacity - len(self.active_shipments)


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            postgresql.UUID(as_uuid=True),
            primary_key=True
        )
    )

    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP,
            server_default=func.now()
        )
    )

    content: str
    weight: float = Field(lt=25)
    destination: int
    status: ShipmentStatus

    estimated_delivery: datetime = Field(
        sa_column=Column(DateTime(timezone=True))
    )

    seller_id: UUID = Field(
        foreign_key="seller.id"
    )

    seller: Seller = Relationship(
        back_populates="shipments"
    )

    delivery_partner_id: UUID | None = Field(
        default=None,
        foreign_key="delivery_partner.id"
    )

    delivery_partner: DeliveryPartner | None = Relationship(
        back_populates="shipments"
    )