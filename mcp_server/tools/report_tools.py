from mcp.server.fastmcp import FastMCP
from database.engine import get_db
from database.models import Order, OrderStatus, Payment, PaymentStatus, Product, CustomerProfile
from sqlalchemy import func
from decimal import Decimal


def register(mcp: FastMCP):

    @mcp.tool(name="get_sales_summary", description="Retorna resumo de vendas: total, pedidos e ticket medio.")
    def get_sales_summary() -> dict:
        with get_db() as db:
            total_orders = db.query(Order).count()
            confirmed = db.query(Order).filter(
                Order.status.in_([
                    OrderStatus.confirmed, OrderStatus.in_production,
                    OrderStatus.ready, OrderStatus.shipped, OrderStatus.delivered,
                ])
            ).count()
            revenue = db.query(func.sum(Payment.amount)).filter(
                Payment.status == PaymentStatus.approved
            ).scalar() or Decimal("0")
            avg_ticket = float(revenue) / confirmed if confirmed else 0
            return {
                "total_orders": total_orders,
                "confirmed_orders": confirmed,
                "total_revenue": float(revenue),
                "average_ticket": round(avg_ticket, 2),
            }

    @mcp.tool(name="get_orders_by_status", description="Conta pedidos agrupados por status.")
    def get_orders_by_status() -> dict:
        with get_db() as db:
            rows = db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()
            return {"by_status": {r[0].value: r[1] for r in rows}}

    @mcp.tool(name="get_low_stock_products", description="Lista produtos com estoque baixo (< 5 unidades).")
    def get_low_stock_products(threshold: int = 5) -> dict:
        with get_db() as db:
            products = db.query(Product).filter(
                Product.is_active == True,
                Product.available_quantity < threshold,
            ).all()
            return {
                "products": [
                    {"id": p.id, "name": p.name, "sku": p.sku,
                     "available_quantity": p.available_quantity}
                    for p in products
                ],
                "count": len(products),
            }

    @mcp.tool(name="get_customer_count", description="Total de clientes cadastrados.")
    def get_customer_count() -> dict:
        with get_db() as db:
            total = db.query(CustomerProfile).count()
            return {"total_customers": total}
