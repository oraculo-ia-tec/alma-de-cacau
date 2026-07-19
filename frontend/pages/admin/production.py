import streamlit as st
from frontend.style import section_header
from database.engine import get_db
from database.models import Order, OrderStatus
from repositories.order_repository import OrderRepository
from services.order_service import OrderService
from schemas.order import OrderStatusUpdate


def render():
    st.markdown(section_header("🍫 Producao", "Pedidos confirmados e em producao"),
                unsafe_allow_html=True)
    with get_db() as db:
        repo = OrderRepository(db)
        confirmed = repo.list_by_status(OrderStatus.confirmed)
        in_prod = repo.list_by_status(OrderStatus.in_production)

    st.markdown(f"### ✅ Confirmados ({len(confirmed)})")
    for o in confirmed:
        col1, col2 = st.columns([4, 2])
        col1.markdown(f"**{o.order_number}** — R$ {float(o.total):.2f}")
        if col2.button("🍫 Iniciar Producao", key=f"prod_{o.id}"):
            data = OrderStatusUpdate(order_id=o.id, new_status=OrderStatus.in_production,
                                     notes="Iniciado na producao.")
            with get_db() as db2:
                OrderService(db2).update_status(data)
            st.rerun()

    st.divider()
    st.markdown(f"### 📦 Em Producao ({len(in_prod)})")
    for o in in_prod:
        col1, col2 = st.columns([4, 2])
        col1.markdown(f"**{o.order_number}** — R$ {float(o.total):.2f}")
        if col2.button("✅ Marcar Pronto", key=f"ready_{o.id}"):
            data = OrderStatusUpdate(order_id=o.id, new_status=OrderStatus.ready,
                                     notes="Producao finalizada.")
            with get_db() as db2:
                OrderService(db2).update_status(data)
            st.rerun()
