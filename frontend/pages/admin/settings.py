import streamlit as st
from frontend.style import section_header


def render():
    st.markdown(section_header("⚙️ Configuracoes"), unsafe_allow_html=True)
    st.info("Configuracoes do sistema serao implementadas em versao futura.")
    st.markdown("- Personalizacao de marca")
    st.markdown("- Taxas de entrega")
    st.markdown("- Configuracoes de notificacao")
    st.markdown("- Backup de dados")
