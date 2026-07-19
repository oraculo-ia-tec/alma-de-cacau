import streamlit as st
from frontend.style import section_header, status_badge
from database.engine import get_db
from database.models import Order, OrderStatus
from repositories.order_repository import OrderRepository
from services.order_service import OrderService
from schemas.order import OrderStatusUpdate
from sqlalchemy import desc

STATUS_OPTIONS = [s.value for s in OrderStatus]


def render():
    st.markdown(section_header("📦 Gestao de Pedidos"), unsafe_allow_html=True)

    filter_status = st.selectbox("Filtrar por status", ["Todos"] + STATUS_OPTIONS)

    with get_db() as db:
        repo = OrderRepository(db)
        if filter_status == "Todos":
            orders = repo.list_all(page_size=50)
        else:
            orders = repo.list_by_status(OrderStatus(filter_status), page_size=50)

    if not orders:
        st.info("Nenhum pedido encontrado.")
        return

    for o in orders:
        with st.expander(
            f"{o.order_number} — R$ {float(o.total):.2f} — {o.created_at.strftime('%d/%m/%Y')}"
        ):
            st.markdown(status_badge(o.status.value), unsafe_allow_html=True)
            st.caption(f"Cliente ID: {o.customer_id} | Entrega: {o.delivery_type.value}")
            new_status = st.selectbox(
                "Alterar status", STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(o.status.value),
                key=f"status_{o.id}",
            )
            notes = st.text_input("Observacao", key=f"notes_{o.id}")
            if st.button("Atualizar Status", key=f"upd_{o.id}"):
                data = OrderStatusUpdate(
                    order_id=o.id, new_status=OrderStatus(new_status),
                    notes=notes, changed_by_user_id=st.session_state.user_id,
                )
                with get_db() as db2:
                    svc = OrderService(db2)
                    _, err = svc.update_status(data)
                    if err:
                        st.error(err)
                    else:
                        st.success("Status atualizado!")
                        st.rerun()
