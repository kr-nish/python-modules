from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Annotated

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class Address(BaseModel):
    street: str
    city: str
    postcode: Annotated[str, Field(pattern=r'^\d{5}$', description="5 digit pincode")]
    country: str = "INDIA"

class Customer(BaseModel):
    id: Annotated[int, Field(gt=0)]
    name: Annotated[str, Field(min_length=3)]
    email: EmailStr
    address: Address

class ItemLine(BaseModel):
    sku: str
    name: str
    quantity: Annotated[int, Field(gt=0)]
    unit_price: float

    @property
    def line_total(self) -> float:
        return self.quantity * self.unit_price

class Payment(BaseModel):
    method: Annotated[str, Field(pattern='^(card|upi|cash)$')]
    transaction_id: Optional[str] = None

class OrderCreate(BaseModel):
    order_id: str
    customer: Customer
    items: List[ItemLine]
    payment: Payment
    notes: Optional[str] = None

    @classmethod
    def validate(cls, values):
        items = values.get("items") or []
        if len(items) == 0:
            raise ValueError("Order must include at least one item")
        payment = values.get("payment")
        if payment and payment.method == "card" and not payment.transaction_id:
            raise ValueError("Card payments require a transaction id")
        return values

class OrderResponse(BaseModel):
    order_id: str
    customer_id: int
    total_amount: float
    items_count: int
