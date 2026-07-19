import streamlit as st
from frontend.style import section_header
from frontend.mcp_client import get_ai_recommendation


def render():
    st.markdown(section_header("🎁 Caixas de Presente",
                               "Surpreenda com sabores artesanais em embalagens especiais"),
                unsafe_allow_html=True)
    st.markdown("""
    Cada caixa e montada à mão com amor e atenção aos detalhes.
    Escolha os sabores, a embalagem e personalize o cartão.
    """)
    if st.button("🧩 Montar minha caixa", use_container_width=True, type="primary"):
        st.session_state.current_page = "build_box"
        st.rerun()
