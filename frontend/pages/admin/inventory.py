import streamlit as st
from frontend.style import section_header
from database.engine import get_db
from repositories.inventory_repository import InventoryRepository
from decimal import Decimal


def render():
    st.markdown(section_header("📎 Estoque", "Controle de ingredientes e insumos"),
                unsafe_allow_html=True)
    with get_db() as db:
        repo = InventoryRepository(db)
        items = repo.list_all()
        low = repo.get_low_stock()

    if low:
        st.warning(f"⚠️ {len(low)} item(s) abaixo do estoque minimo!")
        for i in low:
            st.markdown(f"- **{i.name}**: {float(i.quantity):.1f} {i.unit} (min: {float(i.min_quantity):.1f})")
        st.divider()

    st.markdown("### Todos os Itens")
    for item in items:
        col1, col2, col3 = st.columns([4, 2, 2])
        with col1:
            label = f"⚠️ {item.name}" if item.quantity <= item.min_quantity else item.name
            st.markdown(label)
        with col2:
            st.markdown(f"{float(item.quantity):.2f} {item.unit}")
        with col3:
            delta = st.number_input("", step=0.1, key=f"inv_{item.id}", label_visibility="collapsed")
            if st.button("Ajustar", key=f"adj_{item.id}"):
                with get_db() as db2:
                    repo2 = InventoryRepository(db2)
                    ok, err = repo2.adjust_quantity(item.id, Decimal(str(delta)))
                    if err:
                        st.error(err)
                    else:
                        st.success("Estoque atualizado!")
                        st.rerun()
