import streamlit as st
from frontend.style import section_header
from frontend.mcp_client import get_product_detail
from frontend.components.allergen_badge import allergen_badges
from frontend.state import cart_add, set_notification


def render():
    product_id = st.session_state.get("selected_product_id")
    if not product_id:
        st.warning("Nenhum produto selecionado.")
        return

    p = get_product_detail(product_id)
    if not p:
        st.error("Produto nao encontrado.")
        return

    if st.button("← Voltar ao Catalogo"):
        st.session_state.current_page = "catalog"
        st.rerun()

    st.markdown(section_header(p["name"]), unsafe_allow_html=True)
    st.markdown(f"**R$ {p['price']:.2f}** / {p['unit_label']}")

    if p.get("flavor"):
        f = p["flavor"]
        st.markdown(f"### 🍫 {f['name']}")
        if f.get("tagline"):
            st.markdown(f"*{f['tagline']}*")
        st.markdown(f["description"])
        if f.get("tasting_note"):
            st.info(f"👅 **Como degustar:** {f['tasting_note']}")
        if f.get("pairing_suggestion"):
            st.success(f"🥂 **Harmonizacao:** {f['pairing_suggestion']}")
        if f.get("emotional_context"):
            st.markdown(f"> 💛 {f['emotional_context']}")

    st.divider()
    st.markdown("#### Alergênicos")
    allergen_badges(p.get("allergens", []))

    st.divider()
    qty = st.number_input("Quantidade", min_value=1, max_value=p["available_quantity"], value=1)
    if p["available_quantity"] > 0:
        if st.button("🛒 Adicionar ao Carrinho", use_container_width=True, type="primary"):
            cart_add(product_id=p["id"], name=p["name"], price=p["price"], quantity=qty)
            set_notification(f"{p['name']} adicionado ao carrinho! 🍫")
            st.rerun()
    else:
        st.error("Produto indisponivel no momento.")
