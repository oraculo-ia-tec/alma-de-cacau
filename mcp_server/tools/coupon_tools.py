from mcp.server.fastmcp import FastMCP
from database.engine import get_db
from repositories.coupon_repository import CouponRepository
from database.models import Coupon
from typing import Optional
from datetime import date
from decimal import Decimal


def register(mcp: FastMCP):

    @mcp.tool(name="validate_coupon", description="Valida um cupom de desconto para um subtotal.")
    def validate_coupon(code: str, order_subtotal: float) -> dict:
        with get_db() as db:
            repo = CouponRepository(db)
            coupon, err = repo.validate(code, order_subtotal)
            if err:
                return {"valid": False, "error": err}
            discount = Decimal("0")
            if coupon.discount_percent:
                discount = (Decimal(str(order_subtotal)) * coupon.discount_percent / 100).quantize(Decimal("0.01"))
            elif coupon.discount_fixed:
                discount = min(coupon.discount_fixed, Decimal(str(order_subtotal)))
            return {
                "valid": True,
                "code": coupon.code,
                "discount_amount": float(discount),
                "description": coupon.description,
            }

    @mcp.tool(name="list_active_coupons", description="Lista todos os cupons ativos e validos.")
    def list_active_coupons() -> dict:
        with get_db() as db:
            repo = CouponRepository(db)
            coupons = repo.list_active()
            return {
                "coupons": [
                    {
                        "id": c.id, "code": c.code, "description": c.description,
                        "discount_percent": float(c.discount_percent) if c.discount_percent else None,
                        "discount_fixed": float(c.discount_fixed) if c.discount_fixed else None,
                        "valid_until": c.valid_until.isoformat(),
                        "uses_remaining": (c.max_uses - c.used_count) if c.max_uses else None,
                    }
                    for c in coupons
                ]
            }
