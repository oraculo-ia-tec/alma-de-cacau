import streamlit as st
from frontend.style import section_header
from frontend.mcp_client import get_products
from frontend.components.product_card import product_card
from frontend.components.flavor_selector import flavor_selector


def render():
    st.markdown(section_header("🍫 Catalogo", "Todos os nossos sabores artesanais"),
                unsafe_allow_html=True)

    with st.expander("🔍 Filtros", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            flavor = st.text_input("🍫 Sabor", placeholder="Ex: Caramelo")
        with col2:
            max_p = st.number_input("Preco maximo (R$)", min_value=0.0, value=0.0, step=5.0)
        with col3:
            filter_type = st.radio("Tipo", ["Todos", "Destaques", "Sazonais", "Mais vendidos"],
                                   horizontal=True)

    only_featured = filter_type == "Destaques"
    only_seasonal = filter_type == "Sazonais"
    only_best = filter_type == "Mais vendidos"

    products = get_products(
        flavor_name=flavor or None,
        max_price=max_p if max_p > 0 else None,
        only_featured=only_featured,
        only_seasonal=only_seasonal,
        only_best_sellers=only_best,
    )

    if not products:
        st.info("Nenhum produto encontrado com esses filtros.")
        return

    st.caption(f"{len(products)} produto(s) encontrado(s)")
    cols = st.columns(3)
    for i, p in enumerate(products):
        with cols[i % 3]:
            product_card(p, key_prefix=f"cat{i}")
