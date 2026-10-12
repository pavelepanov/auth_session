from dataclasses import dataclass
from decimal import Decimal
from typing import NewType
from uuid import UUID


from auth.domain.errors import InvalidOrderItemError


PositionId = NewType("PositionId", UUID)
OrderId = NewType("OrderId", UUID)
ProductName = NewType("ProductName", str)
Quantity = NewType("Quantity", int)
UnitPrice = NewType("UnitPrice", Decimal)




@dataclass
class OrderItem:
    id: PositionId
    order_id: OrderId
    product_name: ProductName
    quantity: Quantity
    unit_price: UnitPrice

    def __post_init__(self):
        if self.quantity <= 0:
            raise InvalidOrderItemError("Quantity must be greater than zero.")
        if self.unit_price < 0:
            raise InvalidOrderItemError("Unit price cannot be negative.")

    @property
    def subtotal(self) -> Decimal:
        return self.quantity * self.unit_price


