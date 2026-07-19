from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from datetime import datetime
from database.models import PaymentMethod, PaymentStatus


class CreatePaymentInput(BaseModel):
    order_id: int
    method: PaymentMethod
    asaas_customer_id: Optional[str] = None
    # Nunca receber dados de cartão — usar Asaas Checkout


class PaymentWebhookInput(BaseModel):
    """Payload do webhook Asaas (evento de pagamento)."""
    event: str           # ex: PAYMENT_RECEIVED
    payment: dict        # objeto payment do Asaas


class PaymentOut(BaseModel):
    id: int
    order_id: int
    method: PaymentMethod
    status: PaymentStatus
    amount: Decimal
    provider_reference: Optional[str] = None
    paid_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
