import streamlit as st
from frontend.style import section_header
from database.engine import get_db
from database.models import Order, OrderStatus, Payment, PaymentStatus
from sqlalchemy import func
from decimal import Decimal


def render():
    st.markdown(section_header("📈 Relatorios", "Visao financeira e operacional"),
                unsafe_allow_html=True)
    with get_db() as db:
        revenue = db.query(func.sum(Payment.amount)).filter(
            Payment.status == PaymentStatus.approved
        ).scalar() or Decimal("0")
        by_status = db.query(Order.status, func.count(Order.id)).group_by(Order.status).all()

    st.metric("💰 Receita Total Aprovada", f"R$ {float(revenue):.2f}")
    st.divider()
    st.markdown("### Pedidos por Status")
    for status, count in by_status:
        st.markdown(f"- **{status.value}**: {count} pedido(s)")
