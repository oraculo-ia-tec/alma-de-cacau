"""Leitura segura do status de pagamento para o chat da Cacau."""
from typing import Optional
from database.engine import get_db
from database.models import Payment, PaymentStatus


def payment_is_approved(payment_id: Optional[int] = None, provider_reference: Optional[str] = None) -> bool:
    """Retorna True apenas se o webhook ja tiver gravado approved no banco."""
    if not payment_id and not provider_reference:
        return False

    with get_db() as db:
        query = db.query(Payment)
        if payment_id:
            payment = query.filter(Payment.id == payment_id).first()
        else:
            payment = query.filter(Payment.provider_reference == provider_reference).first()
        return bool(payment and payment.status == PaymentStatus.approved)