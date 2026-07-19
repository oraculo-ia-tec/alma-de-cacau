from sqlalchemy.orm import Session
from database.models import Coupon
from typing import Optional
from datetime import date


class CouponRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_code(self, code: str) -> Optional[Coupon]:
        return self.db.query(Coupon).filter_by(code=code.upper(), is_active=True).first()

    def validate(self, code: str, order_subtotal: float) -> tuple[Optional[Coupon], Optional[str]]:
        from decimal import Decimal
        coupon = self.get_by_code(code)
        if not coupon:
            return None, f"Cupom '{code}' não encontrado ou inativo."
        today = date.today()
        if not (coupon.valid_from <= today <= coupon.valid_until):
            return None, f"Cupom '{code}' fora do período de validade."
        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            return None, f"Cupom '{code}' esgotado."
        if Decimal(str(order_subtotal)) < coupon.min_order_value:
            return None, f"Pedido mínimo de R$ {coupon.min_order_value:.2f} para usar este cupom."
        return coupon, None

    def list_active(self) -> list:
        today = date.today()
        return (
            self.db.query(Coupon)
            .filter(
                Coupon.is_active == True,
                Coupon.valid_from <= today,
                Coupon.valid_until >= today,
            )
            .all()
        )
