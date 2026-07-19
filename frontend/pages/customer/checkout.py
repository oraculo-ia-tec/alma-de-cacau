import streamlit as st
from frontend.style import section_header
from frontend.state import cart_total, cart_clear, set_notification
from frontend.mcp_client import create_order


def render():
    st.markdown(section_header("🛒 Finalizar Pedido"), unsafe_allow_html=True)

    cart = st.session_state.cart
    if not cart:
        st.warning("Carrinho vazio.")
        return
    if not st.session_state.customer_id:
        st.error("Voce precisa estar logado para finalizar o pedido.")
        return

    st.markdown("#### Resumo do Pedido")
    for item in cart:
        st.markdown(f"- {item['name']} x{item['quantity']} — R$ {item['price'] * item['quantity']:.2f}")
    st.markdown(f"**Total: R$ {cart_total():.2f}**")

    st.divider()
    delivery_type = st.radio("Entrega", ["Retirada na loja (pickup)", "Entrega (delivery)"])
    coupon = st.text_input("🎫 Cupom de desconto (opcional)")
    notes = st.text_area("📝 Observacoes", placeholder="Alergias, data especial, etc.")

    if st.button("✅ Confirmar Pedido", use_container_width=True, type="primary"):
        dtype = "pickup" if "pickup" in delivery_type else "delivery"
        result = create_order(
            customer_id=st.session_state.customer_id,
            cart_items=cart,
            coupon_code=coupon or None,
            delivery_type=dtype,
            customer_notes=notes or None,
        )
        if "error" in result:
            st.error(result["error"])
        else:
            cart_clear()
            st.session_state.last_order_number = result["order_number"]
            set_notification(f"Pedido {result['order_number']} criado com sucesso! 🍫")
            st.session_state.current_page = "order_tracking"
            st.rerun()
