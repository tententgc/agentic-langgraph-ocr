from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class Address(BaseModel):
    name: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

class LineItem(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0
    discount: float = 0.0
    tax_rate: float = 0.0

    @property
    def subtotal(self) -> float:
        return max(0.0, self.quantity * self.unit_price - self.discount)

    @property
    def tax_amount(self) -> float:
        return self.subtotal * (self.tax_rate / 100.0)

class Invoice(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    seller: Address = Field(default_factory=Address)
    buyer: Address = Field(default_factory=Address)
    currency: str = "THB"
    line_items: List[LineItem] = Field(default_factory=list)
    subtotal: float = 0.0
    tax_total: float = 0.0
    total: float = 0.0
    notes: Optional[str] = None

    @field_validator("currency")
    @classmethod
    def norm_currency(cls, v: str) -> str:
        return (v or "THB").upper().strip()
