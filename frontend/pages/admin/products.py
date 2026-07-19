import streamlit as st
from frontend.style import section_header
from frontend.mcp_client import get_products
from database.engine import get_db
from database.models import Product
from services.product_service import ProductService


def render():
    st.markdown(section_header("🍫 Gestao de Produtos"), unsafe_allow_html=True)

    products = get_products(page_size=50)
    if not products:
        st.info("Nenhum produto cadastrado.")
        return

    for p in products:
        with st.expander(f"{p['name']} — R$ {p['price']:.2f} — SKU: {p['sku']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Estoque", p["available_quantity"])
                delta = st.number_input("Ajuste de estoque", step=1, key=f"delta_{p['id']}")
                if st.button("Aplicar", key=f"stock_{p['id']}"):
                    with get_db() as db:
                        svc = ProductService(db)
                        ok, err = svc.update_stock(p["id"], int(delta))
                        if err:
                            st.error(err)
                        else:
                            st.success("Estoque atualizado!")
                            st.rerun()
            with col2:
                status_label = "Ativo" if True else "Inativo"
                if st.button(f"Alternar Status", key=f"toggle_{p['id']}"):
                    with get_db() as db:
                        svc = ProductService(db)
                        new_status, err = svc.toggle_active(p["id"])
                        if err:
                            st.error(err)
                        else:
                            st.success(f"Produto {'ativado' if new_status else 'desativado'}!")
                            st.rerun()
