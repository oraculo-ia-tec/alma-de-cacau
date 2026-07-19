"""
Cliente que chama as ferramentas MCP diretamente (em processo).
Em modo producao pode ser substituido por chamadas HTTP ao servidor MCP.
"""
from database.engine import get_db, init_db
from repositories.product_repository import ProductRepository
from repositories.order_repository import OrderRepository
from schemas.product import ProductFilterInput
from services.order_service import OrderService
from services.customer_service import CustomerService
from services.gift_service import GiftService
from services.payment_service import PaymentService
from services.notification_service import NotificationService
from services.ai_service import AIService
from schemas.order import CreateOrderInput, OrderItemInput, OrderStatusUpdate
from schemas.customer import CreateCustomerInput, AddressInput
from schemas.gift import CreateGiftBoxInput
from schemas.payment import CreatePaymentInput
from database.models import DeliveryType, PaymentMethod, NotificationChannel, OrderStatus
from typing import Optional, List
from decimal import Decimal
import os

import config
init_db()


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CATALOGO
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def get_products(flavor_name=None, max_price=None, only_featured=False,
                 only_seasonal=False, only_best_sellers=False,
                 page=1, page_size=12) -> list:
    filters = ProductFilterInput(
        flavor_name=flavor_name,
        max_price=Decimal(str(max_price)) if max_price else None,
        only_featured=only_featured,
        only_seasonal=only_seasonal,
        only_best_sellers=only_best_sellers,
        page=page, page_size=page_size,
    )
    with get_db() as db:
        repo = ProductRepository(db)
        products = repo.list_products(filters)
        return [
            {
                "id": p.id, "sku": p.sku, "name": p.name,
                "price": float(p.price), "unit_label": p.unit_label,
                "is_featured": p.is_featured, "is_best_seller": p.is_best_seller,
                "is_seasonal": p.is_seasonal,
                "available_quantity": p.available_quantity,
                "flavor_name": p.flavor.name if p.flavor else None,
                "flavor_tagline": p.flavor.tagline if p.flavor else None,
                "allergens": [
                    {"name": a.allergen.name, "icon": a.allergen.icon, "is_trace": a.is_trace}
                    for a in p.allergens
                ],
                "image_url": p.image_url,
            }
            for p in products
        ]


def get_product_detail(product_id: int) -> Optional[dict]:
    with get_db() as db:
        repo = ProductRepository(db)
        p = repo.get_by_id(product_id)
        if not p:
            return None
        return {
            "id": p.id, "sku": p.sku, "name": p.name, "description": p.description,
            "price": float(p.price), "unit_label": p.unit_label,
            "available_quantity": p.available_quantity,
            "flavor": {
                "name": p.flavor.name, "tagline": p.flavor.tagline,
                "description": p.flavor.description, "tasting_note": p.flavor.tasting_note,
                "pairing_suggestion": p.flavor.pairing_suggestion,
                "emotional_context": p.flavor.emotional_context,
            } if p.flavor else None,
            "allergens": [
                {"name": a.allergen.name, "icon": a.allergen.icon,
                 "is_trace": a.is_trace,
                 "label": f"Pode conter: {a.allergen.name}" if a.is_trace else f"Contem: {a.allergen.name}"}
                for a in p.allergens
            ],
            "is_featured": p.is_featured, "is_best_seller": p.is_best_seller,
            "is_seasonal": p.is_seasonal, "image_url": p.image_url,
        }


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PEDIDOS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def create_order(customer_id: int, cart_items: list,
                 coupon_code: Optional[str] = None,
                 delivery_type: str = "pickup",
                 delivery_address_id: Optional[int] = None,
                 customer_notes: Optional[str] = None) -> dict:
    items = [OrderItemInput(product_id=i["product_id"], quantity=i["quantity"]) for i in cart_items]
    data = CreateOrderInput(
        customer_id=customer_id, items=items,
        delivery_type=DeliveryType(delivery_type),
        delivery_address_id=delivery_address_id,
        coupon_code=coupon_code, customer_notes=customer_notes,
    )
    with get_db() as db:
        svc = OrderService(db)
        order, err = svc.create_order(data)
        if err:
            return {"error": err}
        return {
            "success": True, "order_id": order.id,
            "order_number": order.order_number,
            "total": float(order.total), "status": order.status.value,
        }


def get_order_by_number(order_number: str) -> Optional[dict]:
    with get_db() as db:
        repo = OrderRepository(db)
        o = repo.get_by_order_number(order_number)
        if not o:
            return None
        return {
            "order_number": o.order_number, "status": o.status.value,
            "total": float(o.total), "delivery_type": o.delivery_type.value,
            "history": [
                {"from": h.previous_status.value if h.previous_status else None,
                 "to": h.new_status.value, "at": h.changed_at.isoformat()}
                for h in sorted(o.status_history, key=lambda x: x.changed_at)
            ],
        }


def get_customer_orders(customer_id: int) -> list:
    with get_db() as db:
        repo = OrderRepository(db)
        orders = repo.list_by_customer(customer_id)
        return [
            {"order_number": o.order_number, "status": o.status.value,
             "total": float(o.total), "created_at": o.created_at.isoformat()}
            for o in orders
        ]


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# AUTENTICACAO
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def login(email: str, password: str) -> dict:
    with get_db() as db:
        svc = CustomerService(db)
        user, err = svc.authenticate(email, password)
        if err:
            return {"error": err}
        profile = db.query(__import__("database.models", fromlist=["CustomerProfile"]).CustomerProfile)\
            .filter_by(user_id=user.id).first()
        return {
            "success": True, "user_id": user.id,
            "customer_id": profile.id if profile else None,
            "full_name": user.full_name, "email": user.email,
            "is_admin": user.role.value in ("admin", "operator"),
        }


def register_customer(full_name: str, email: str, password: str,
                      phone: Optional[str] = None) -> dict:
    data = CreateCustomerInput(full_name=full_name, email=email, password=password, phone=phone)
    with get_db() as db:
        svc = CustomerService(db)
        profile, err = svc.register(data)
        if err:
            return {"error": err}
        return {"success": True, "customer_id": profile.id}


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# IA
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def get_ai_recommendation(occasion: str, preferences: list = None,
                          restrictions: list = None) -> str:
    svc = AIService()
    return svc.get_flavor_recommendations(
        occasion=occasion,
        preferences=preferences or [],
        restrictions=restrictions or [],
    )


def get_gift_message_ai(sender: str, recipient: str,
                        occasion: str, tone: str = "afetuoso") -> str:
    svc = AIService()
    return svc.get_gift_message(sender=sender, recipient=recipient,
                                occasion=occasion, tone=tone)

