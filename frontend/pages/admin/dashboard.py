import streamlit as st
from frontend.style import section_header
from frontend.mcp_client import get_db
from database.models import Order, OrderStatus, Payment, PaymentStatus, Product, CustomerProfile
from sqlalchemy import func
from database.engine import get_db
from decimal import Decimal


def render():
    st.markdown(section_header("📊 Dashboard", "Visao geral da Alma de Cacau"),
                unsafe_allow_html=True)
    with get_db() as db:
        total_orders = db.query(Order).count()
        pending = db.query(Order).filter_by(status=OrderStatus.pending).count()
        in_prod = db.query(Order).filter_by(status=OrderStatus.in_production).count()
        revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.approved
        ).scalar() or Decimal("0")
        total_customers = db.query(CustomerProfile).count()
        low_stock = db.query(Product).filter(
            Product.is_active == True, Product.available_quantity < 5
        ).count()

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total de Pedidos", total_orders)
    col2.metric("⏳ Pendentes", pending)
    col3.metric("🍫 Em Producao", in_prod)

    col4, col5, col6 = st.columns(3)
    col4.metric("💰 Receita Aprovada", f"R$ {float(revenue):.2f}")
    col5.metric("🧑 Clientes", total_customers)
    col6.metric("⚠️ Estoque Baixo", low_stock)

    st.divider()
    st.markdown("### 📦 Ultimos Pedidos")
    with get_db() as db:
        from sqlalchemy import desc
        orders = db.query(Order).order_by(desc(Order.created_at)).limit(10).all()
        if orders:
            for o in orders:
                st.markdown(
                    f"`{o.order_number}` — **{o.status.value}** — "
                    f"R$ {float(o.total):.2f} — {o.created_at.strftime('%d/%m/%Y %H:%M')}"
                )
