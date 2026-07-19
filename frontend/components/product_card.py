import streamlit as st
from frontend.style import product_card_html
from frontend.components.allergen_badge import allergen_badges
from frontend.state import cart_add, set_notification


def product_card(product: dict, show_add_button: bool = True, key_prefix: str = ""):
    prefix = f"{key_prefix}_" if key_prefix else ""
    st.markdown(product_card_html(product), unsafe_allow_html=True)
    if product.get("allergens"):
        allergen_badges(product["allergens"])
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("👁️ Ver detalhes", key=f"{prefix}detail_{product['id']}",
                     use_container_width=True):
            st.session_state.selected_product_id = product["id"]
            st.session_state.current_page = "product_detail"
            st.rerun()
    with col2:
        if show_add_button and product.get("available_quantity", 0) > 0:
            if st.button("➕", key=f"{prefix}add_{product['id']}"):
                cart_add(
                    product_id=product["id"],
                    name=product["name"],
                    price=product["price"],
                )
                set_notification(f"{product['name']} adicionado ao carrinho! 🍫")
                st.rerun()
