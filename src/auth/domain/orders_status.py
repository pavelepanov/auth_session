from enum import StrEnum

class OrderStatus(StrEnum):
    NEW = "new"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
