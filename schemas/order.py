from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List
from database.models import OrderStatus, DeliveryType, PaymentMethod


class OrderItemInput(BaseModel):
    product_id: Optional[int] = None
    gift_box_id: Optional[int] = None
    quantity: int = Field(ge=1)
    item_notes: Optional[str] = None


class CreateOrderInput(BaseModel):
    customer_id: int
    items: List[OrderItemInput] = Field(min_length=1)
    delivery_type: DeliveryType = DeliveryType.pickup
    delivery_address_id: Optional[int] = None
    coupon_code: Optional[str] = None
    customer_notes: Optional[str] = None
    desired_delivery_date: Optional[str] = None  # ISO date string


class OrderStatusUpdate(BaseModel):
    order_id: int
    new_status: OrderStatus
    notes: Optional[str] = None
    changed_by_user_id: Optional[int] = None


class OrderOut(BaseModel):
    id: int
    order_number: str
    status: OrderStatus
    subtotal: Decimal
    discount_amount: Decimal
    shipping_cost: Decimal
    total: Decimal
    delivery_type: DeliveryType
    items_count: int

    model_config = {"from_attributes": True}
