import streamlit as st
from frontend.style import section_header
from frontend.mcp_client import login, register_customer
from frontend.state import set_notification


def render():
    st.markdown(section_header("👤 Minha Conta"), unsafe_allow_html=True)

    if st.session_state.user_id:
        st.success(f"Bem-vindo(a), {st.session_state.customer_name}! 🍫")
        if st.button("🚪 Sair da conta"):
            for k in ["user_id", "customer_id"]:
                st.session_state[k] = None
            st.session_state.customer_name = ""
            st.session_state.is_admin = False
            st.rerun()
        return

    tab_login, tab_register = st.tabs(["🔑 Entrar", "🌟 Cadastrar"])

    with tab_login:
        with st.form("form_login"):
            email = st.text_input("📧 E-mail")
            password = st.text_input("🔒 Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                if not email or not password:
                    st.error("Preencha e-mail e senha.")
                else:
                    result = login(email, password)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state.user_id = result["user_id"]
                        st.session_state.customer_id = result["customer_id"]
                        st.session_state.customer_name = result["full_name"]
                        st.session_state.customer_email = result["email"]
                        st.session_state.is_admin = result["is_admin"]
                        set_notification(f"Bem-vindo(a), {result['full_name'].split()[0]}! 🍫")
                        st.rerun()

    with tab_register:
        with st.form("form_register"):
            full_name = st.text_input("👤 Nome completo")
            email_r = st.text_input("📧 E-mail", key="reg_email")
            phone = st.text_input("📱 Telefone (opcional)")
            password_r = st.text_input("🔒 Senha (min. 8 caracteres)", type="password", key="reg_pass")
            marketing = st.checkbox("📩 Quero receber novidades e promocoes")
            if st.form_submit_button("Cadastrar", use_container_width=True):
                if not all([full_name, email_r, password_r]):
                    st.error("Preencha nome, e-mail e senha.")
                elif len(password_r) < 8:
                    st.error("Senha deve ter pelo menos 8 caracteres.")
                else:
                    result = register_customer(full_name, email_r, password_r, phone or None)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        set_notification("Cadastro realizado! Faca login para continuar. 🍫")
                        st.rerun()
