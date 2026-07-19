import streamlit as st
from frontend.style import section_header
from database.engine import get_db
from repositories.customer_repository import CustomerRepository


def render():
    st.markdown(section_header("🧑‍🤝‍🧑 Clientes"), unsafe_allow_html=True)
    with get_db() as db:
        repo = CustomerRepository(db)
        customers = repo.list_all(page_size=50)
    if not customers:
        st.info("Nenhum cliente cadastrado.")
        return
    for c in customers:
        with st.expander(f"{c.user.full_name} — {c.user.email}"):
            st.markdown(f"**Telefone:** {c.phone or 'nao informado'}")
            st.markdown(f"**Consentimento marketing:** {'Sim' if c.marketing_consent else 'Nao'}")
            st.markdown(f"**Enderecos:** {len(c.addresses)}")
