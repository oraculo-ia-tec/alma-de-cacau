import streamlit as st
from frontend.style import section_header
from frontend.mcp_client import get_order_by_number, get_customer_orders
from frontend.components.order_timeline import order_timeline


def render():
    st.markdown(section_header("📦 Acompanhar Pedido"), unsafe_allow_html=True)

    if st.session_state.customer_id:
        st.markdown("#### Meus Pedidos")
        orders = get_customer_orders(st.session_state.customer_id)
        if orders:
            for o in orders:
                with st.expander(f"📦 {o['order_number']} — R$ {o['total']:.2f}"):
                    detail = get_order_by_number(o["order_number"])
                    if detail:
                        order_timeline(detail["history"])
        else:
            st.info("Nenhum pedido encontrado.")
        st.divider()

    st.markdown("#### Buscar pedido pelo numero")
    order_number = st.text_input("🔍 Numero do pedido", placeholder="ADC-20240101-XXXXXX")
    if st.button("Buscar"):
        if order_number:
            order = get_order_by_number(order_number)
            if not order:
                st.error("Pedido nao encontrado.")
            else:
                st.success(f"Pedido {order['order_number']} encontrado!")
                st.markdown(f"**Status:** {order['status']}")
                st.markdown(f"**Total:** R$ {order['total']:.2f}")
                st.markdown("**Historico:**")
                order_timeline(order["history"])
