from mcp.server.fastmcp import FastMCP
from database.engine import get_db
from database.models import Order, OrderStatus, CustomerProfile
from services.order_service import OrderService
from schemas.order import CreateOrderInput, OrderStatusUpdate, OrderItemInput
from database.models import DeliveryType
from typing import Optional, List


def register(mcp: FastMCP):

    @mcp.tool(
        name="create_order",
        description="""
        Cria um novo pedido para um cliente.

        ENTRADA:
        - customer_id (int): ID do cliente
        - items (list): lista de {product_id?, gift_box_id?, quantity, item_notes?}
        - delivery_type (str): "pickup" ou "delivery"
        - delivery_address_id (int, opcional): obrigatório se delivery
        - coupon_code (str, opcional): código do cupom
        - customer_notes (str, opcional): observações do cliente
        - desired_delivery_date (str, opcional): data desejada ISO (YYYY-MM-DD)

        SAÍDA: Pedido criado com número, total e status.

        REGRAS:
        - Estoque é verificado e decrementado atomicamente.
        - Preço é snapshot do momento da compra.
        - Cupom é validado antes da criação.
        - Pedido com delivery exige endereço.

        ERROS:
        - Estoque insuficiente, produto inativo, cupom inválido, endereço ausente.
        """,
    )
    def create_order(
        customer_id: int,
        items: List[dict],
        delivery_type: str = "pickup",
        delivery_address_id: Optional[int] = None,
        coupon_code: Optional[str] = None,
        customer_notes: Optional[str] = None,
        desired_delivery_date: Optional[str] = None,
    ) -> dict:
        if delivery_type == "delivery" and not delivery_address_id:
            return {"error": "Endereço de entrega é obrigatório para pedidos com delivery."}

        parsed_items = []
        for it in items:
            parsed_items.append(OrderItemInput(
                product_id=it.get("product_id"),
                gift_box_id=it.get("gift_box_id"),
                quantity=it.get("quantity", 1),
                item_notes=it.get("item_notes"),
            ))

        data = CreateOrderInput(
            customer_id=customer_id,
            items=parsed_items,
            delivery_type=DeliveryType(delivery_type),
            delivery_address_id=delivery_address_id,
            coupon_code=coupon_code,
            customer_notes=customer_notes,
            desired_delivery_date=desired_delivery_date,
        )

        with get_db() as db:
            service = OrderService(db)
            order, error = service.create_order(data)
            if error:
                return {"error": error}
            return {
                "success": True,
                "order_id": order.id,
                "order_number": order.order_number,
                "status": order.status.value,
                "subtotal": float(order.subtotal),
                "discount_amount": float(order.discount_amount),
                "shipping_cost": float(order.shipping_cost),
                "total": float(order.total),
                "message": f"Pedido {order.order_number} criado com sucesso! 🍫",
            }

    @mcp.tool(name="get_order_status", description="Retorna o status atual e histórico de um pedido pelo número.")
    def get_order_status(order_number: str) -> dict:
        with get_db() as db:
            order = db.query(Order).filter_by(order_number=order_number).first()
            if not order:
                return {"error": f"Pedido {order_number} não encontrado."}
            history = [
                {
                    "from": h.previous_status.value if h.previous_status else None,
                    "to": h.new_status.value,
                    "at": h.changed_at.isoformat(),
                    "notes": h.notes,
                }
                for h in sorted(order.status_history, key=lambda x: x.changed_at)
            ]
            return {
                "order_number": order.order_number,
                "status": order.status.value,
                "total": float(order.total),
                "delivery_type": order.delivery_type.value,
                "history": history,
            }

    @mcp.tool(
        name="cancel_order",
        description="""
        Cancela um pedido. Permitido apenas nos status: pending e confirmed.

        ENTRADA: order_id (int), reason (str), user_id (int)

        REGRAS:
        - Pedidos in_production ou posteriores não podem ser cancelados via sistema.
        - O estoque é devolvido ao cancelar.

        ERROS: Pedido não encontrado, status não permite cancelamento.
        """,
    )
    def cancel_order(order_id: int, reason: str, user_id: Optional[int] = None) -> dict:
        with get_db() as db:
            service = OrderService(db)
            data = OrderStatusUpdate(
                order_id=order_id,
                new_status=OrderStatus.cancelled,
                notes=f"Cancelamento: {reason}",
                changed_by_user_id=user_id,
            )
            order, error = service.update_status(data)
            if error:
                return {"error": error}
            # Devolver estoque
            for item in order.items:
                if item.product_id:
                    product = item.product
                    if product:
                        product.available_quantity += item.quantity
            return {"success": True, "message": f"Pedido {order.order_number} cancelado.", "order_number": order.order_number}
