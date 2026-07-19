from sqlalchemy.orm import Session
from database.models import Payment, Order, PaymentStatus, PaymentMethod
from schemas.payment import CreatePaymentInput
from adapters.asaas_adapter import (
    create_payment as asaas_create_payment,
    get_pix_qr_code,
    refund_payment as asaas_refund,
    map_asaas_status,
)
from typing import Optional, Tuple
from datetime import datetime


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def create_payment(self, data: CreatePaymentInput) -> Tuple[Optional[Payment], Optional[str]]:
        order = self.db.query(Order).filter_by(id=data.order_id).first()
        if not order:
            return None, "Pedido nao encontrado."
        if self.db.query(Payment).filter_by(order_id=data.order_id).first():
            return None, "Pagamento ja registrado para este pedido."

        provider_reference = None
        provider_status = None

        if data.method in (PaymentMethod.asaas, PaymentMethod.pix, PaymentMethod.boleto):
            if not data.asaas_customer_id:
                return None, "asaas_customer_id obrigatorio para pagamentos via Asaas."
            billing_map = {
                PaymentMethod.pix: "PIX",
                PaymentMethod.boleto: "BOLETO",
                PaymentMethod.asaas: "UNDEFINED",
            }
            billing_type = billing_map.get(data.method, "UNDEFINED")
            result, err = asaas_create_payment(
                asaas_customer_id=data.asaas_customer_id,
                amount=float(order.total),
                billing_type=billing_type,
                description=f"Pedido {order.order_number} - Alma de Cacau",
                external_reference=order.order_number,
            )
            if err:
                return None, f"Erro Asaas: {err}"
            provider_reference = result.get("id")
            provider_status = result.get("status")

        payment = Payment(
            order_id=order.id,
            method=data.method,
            status=PaymentStatus.pending,
            amount=order.total,
            provider_reference=provider_reference,
            provider_status=provider_status,
        )
        self.db.add(payment)
        return payment, None

    def get_pix_qr_code(self, payment_id: int) -> Tuple[Optional[dict], Optional[str]]:
        payment = self.db.query(Payment).filter_by(id=payment_id).first()
        if not payment or not payment.provider_reference:
            return None, "Pagamento ou referencia Asaas nao encontrada."
        return get_pix_qr_code(payment.provider_reference)

    def confirm_payment(self, asaas_payment_id: str, asaas_status: str) -> Tuple[bool, Optional[str]]:
        payment = self.db.query(Payment).filter_by(provider_reference=asaas_payment_id).first()
        if not payment:
            return False, "Pagamento nao encontrado."
        internal_status = map_asaas_status(asaas_status)
        payment.status = PaymentStatus(internal_status)
        payment.provider_status = asaas_status
        if internal_status == "approved":
            payment.paid_at = datetime.utcnow()
        return True, None

    def refund(self, payment_id: int) -> Tuple[bool, Optional[str]]:
        payment = self.db.query(Payment).filter_by(id=payment_id).first()
        if not payment:
            return False, "Pagamento nao encontrado."
        if payment.status != PaymentStatus.approved:
            return False, "Somente pagamentos aprovados podem ser estornados."
        if payment.provider_reference:
            _, err = asaas_refund(payment.provider_reference)
            if err:
                return False, f"Erro no estorno Asaas: {err}"
        payment.status = PaymentStatus.refunded
        payment.refunded_at = datetime.utcnow()
        return True, None
