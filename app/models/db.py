from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session
from app.core.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Invoice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_number: str = Field(index=True)
    invoice_identifier: str = Field(index=True, unique=True)
    invoice_date: str
    invoice_type: str
    invoice_registered_number: str
    invoice_registered_date: str
    electronic_signature: str
    cancelled: bool = False
    raw_json: str  # stocke le payload complet


class StockMovement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    system_or_device_id: str
    item_code: str
    item_designation: str
    item_quantity: str
    item_measurement_unit: str
    item_purchase_or_sale_price: str
    item_purchase_or_sale_currency: str
    item_movement_type: str
    item_movement_invoice_ref: Optional[str] = ""
    item_movement_description: Optional[str] = ""
    item_movement_date: str


def get_session():
    with Session(engine) as session:
        yield session


def create_db():
    SQLModel.metadata.create_all(engine)
