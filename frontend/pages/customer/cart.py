import streamlit as st
from frontend.style import section_header
from frontend.state import cart_remove, cart_clear, cart_total, set_notification


def render():
    st.markdown(section_header("🛒 Carrinho"), unsafe_allow_html=True)

    cart = st.session_state.cart
    if not cart:
        st.info("Seu carrinho esta vazio. Que tal explorar nosso catalogo? 🍫")
        if st.button("🔍 Ver Catalogo"):
            st.session_state.current_page = "catalog"
            st.rerun()
        return

    for item in cart:
        col1, col2, col3 = st.columns([5, 2, 1])
        with col1:
            st.markdown(f"**{item['name']}**")
            st.caption(f"R$ {item['price']:.2f} x {item['quantity']}")
        with col2:
            st.markdown(f"**R$ {item['price'] * item['quantity']:.2f}**")
        with col3:
            if st.button("🗑️", key=f"rm_{item['product_id']}"):
                cart_remove(item["product_id"])
                st.rerun()
        st.divider()

    total = cart_total()
    st.markdown(f"### Total: **R$ {total:.2f}**")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Limpar Carrinho", use_container_width=True):
            cart_clear()
            st.rerun()
    with col2:
        if st.session_state.customer_id:
            if st.button("🛒 Finalizar Pedido", use_container_width=True, type="primary"):
                st.session_state.current_page = "checkout"
                st.rerun()
        else:
            st.warning("Faca login para finalizar o pedido.")
            if st.button("🔑 Entrar / Cadastrar", use_container_width=True):
                st.session_state.current_page = "my_account"
                st.rerun()
