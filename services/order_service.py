from sqlalchemy.orm import Session
from database.models import (
    Order, OrderItem, OrderStatus, OrderStatusHistory,
    Product, GiftBox, Coupon, DeliveryType,
)
from schemas.order import CreateOrderInput, OrderStatusUpdate
from typing import Optional, Tuple
from decimal import Decimal
from datetime import datetime, date
import uuid


def _generate_order_number() -> str:
    return f"ADC-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, data: CreateOrderInput) -> Tuple[Optional[Order], Optional[str]]:
        if data.delivery_type == DeliveryType.delivery and not data.delivery_address_id:
            return None, "Endereco obrigatorio para pedidos com entrega."

        subtotal = Decimal("0")
        discount = Decimal("0")
        order_items_data = []

        for item_input in data.items:
            if item_input.product_id:
                product = (
                    self.db.query(Product)
                    .filter_by(id=item_input.product_id, is_active=True)
                    .with_for_update()
                    .first()
                )
                if not product:
                    return None, f"Produto {item_input.product_id} nao encontrado ou inativo."
                if product.available_quantity < item_input.quantity:
                    return None, f"Estoque insuficiente para '{product.name}'."
                unit_price = product.price
                total = unit_price * item_input.quantity
                product.available_quantity -= item_input.quantity
                order_items_data.append(dict(
                    product_id=product.id, gift_box_id=None,
                    quantity=item_input.quantity, unit_price_snapshot=unit_price,
                    total_price=total, item_notes=item_input.item_notes,
                ))
                subtotal += total
            elif item_input.gift_box_id:
                gift_box = self.db.query(GiftBox).filter_by(id=item_input.gift_box_id, is_active=True).first()
                if not gift_box:
                    return None, f"Caixa de presente {item_input.gift_box_id} nao encontrada."
                items_total = sum(i.unit_price_snapshot * i.quantity for i in gift_box.items)
                unit_price = gift_box.packaging_price + items_total
                total = unit_price * item_input.quantity
                order_items_data.append(dict(
                    product_id=None, gift_box_id=gift_box.id,
                    quantity=item_input.quantity, unit_price_snapshot=unit_price,
                    total_price=total, item_notes=item_input.item_notes,
                ))
                subtotal += total
            else:
                return None, "Cada item precisa de product_id ou gift_box_id."

        coupon_id = None
        if data.coupon_code:
            coupon = self.db.query(Coupon).filter_by(code=data.coupon_code.upper(), is_active=True).first()
            if not coupon:
                return None, f"Cupom '{data.coupon_code}' invalido."
            today = date.today()
            if not (coupon.valid_from <= today <= coupon.valid_until):
                return None, f"Cupom '{data.coupon_code}' fora da validade."
            if coupon.max_uses and coupon.used_count >= coupon.max_uses:
                return None, f"Cupom '{data.coupon_code}' esgotado."
            if subtotal < coupon.min_order_value:
                return None, f"Minimo de R$ {coupon.min_order_value:.2f} para este cupom."
            if coupon.discount_percent:
                discount = (subtotal * coupon.discount_percent / 100).quantize(Decimal("0.01"))
            elif coupon.discount_fixed:
                discount = min(coupon.discount_fixed, subtotal)
            coupon.used_count += 1
            coupon_id = coupon.id

        desired_date = None
        if data.desired_delivery_date:
            try:
                desired_date = date.fromisoformat(data.desired_delivery_date)
            except ValueError:
                return None, "Data invalida. Use YYYY-MM-DD."

        total = subtotal - discount
        order = Order(
            order_number=_generate_order_number(),
            customer_id=data.customer_id,
            delivery_type=data.delivery_type,
            delivery_address_id=data.delivery_address_id,
            status=OrderStatus.pending,
            subtotal=subtotal,
            discount_amount=discount,
            shipping_cost=Decimal("0"),
            total=total,
            coupon_id=coupon_id,
            customer_notes=data.customer_notes,
            desired_delivery_date=desired_date,
        )
        self.db.add(order)
        self.db.flush()

        for item_data in order_items_data:
            self.db.add(OrderItem(order_id=order.id, **item_data))

        self.db.add(OrderStatusHistory(
            order_id=order.id, previous_status=None,
            new_status=OrderStatus.pending, notes="Pedido criado.",
        ))
        return order, None

    def update_status(self, data: OrderStatusUpdate) -> Tuple[Optional[Order], Optional[str]]:
        order = self.db.query(Order).filter_by(id=data.order_id).with_for_update().first()
        if not order:
            return None, f"Pedido {data.order_id} nao encontrado."
        if data.new_status == OrderStatus.cancelled:
            if order.status not in (OrderStatus.pending, OrderStatus.confirmed):
                return None, f"Status '{order.status.value}' nao permite cancelamento."
        self.db.add(OrderStatusHistory(
            order_id=order.id, previous_status=order.status,
            new_status=data.new_status,
            changed_by_user_id=data.changed_by_user_id,
            notes=data.notes,
        ))
        order.status = data.new_status
        return order, None
