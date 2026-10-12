from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID
from typing import NewType

from decimal import Decimal


from auth.domain.entities.order_item import  OrderId, ProductName, Quantity, UnitPrice, OrderItem
from auth.domain.entities.user import UserId
from auth.domain.orders_status import OrderStatus
from auth.domain.errors import EmptyOrderError, OrderStateError

CreatedAt = NewType("CreatedAt", datetime)
UpdatedAt = NewType("UpdatedAt", datetime)
CancelReason = NewType("CancelReason", str )

@dataclass
class Order:
    id: OrderId
    user_id: UserId
    items: list[OrderItem]
    status: OrderStatus
    created_at: CreatedAt
    updated_at: UpdatedAt
    cancel_reason: CancelReason | None

    @property
    def total_amount(self) -> Decimal:
        return sum(item.subtotal for item in self.items)


    def confirm(self) -> None:
        if self.status != OrderStatus.NEW:
            raise OrderStateError("Only new orders can be confirmed.")
        
        self.status = OrderStatus.CONFIRMED
        self.updated_at = UpdatedAt(datetime.now(timezone.utc))


    def cancel(self, reason: CancelReason) -> None:
        if self.status != OrderStatus.NEW:
            raise OrderStateError("Only new orders can be cancelled.")
        
        if not reason.strip():
            raise OrderStateError("The cancellation reason cannot be an empty string.")
        
        self.status = OrderStatus.CANCELLED
        self.cancel_reason = reason
        self.updated_at = UpdatedAt(datetime.now(timezone.utc))
    
        


def create_order(
    id: OrderId,
    user_id: UserId,
    items: list[OrderItem],
) -> Order:
    if not items:
        raise EmptyOrderError("Order must have at least one item.")

    now = CreatedAt(datetime.now(timezone.utc))
    return Order(
        id=id,
        user_id=user_id,
        items=items,
        status=OrderStatus.NEW,
        created_at=now,
        updated_at=UpdatedAt(now),
        cancel_reason=None,    
    )

