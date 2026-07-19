import streamlit as st
from frontend.style import section_header


def render():
    st.markdown(section_header("📞 Contato",
                               "Feito a mao, com carinho — estamos aqui para voce"),
                unsafe_allow_html=True)
    st.markdown("""
    **Alma de Cacau**
    Chocolates artesanais feitos com amor.

    📧 contato@almadecacau.com.br
    📱 WhatsApp: (xx) xxxxx-xxxx
    📍 Retirada com hora marcada
    """)
    with st.form("contact_form"):
        name = st.text_input("Seu nome")
        email = st.text_input("Seu e-mail")
        msg = st.text_area("Mensagem")
        if st.form_submit_button("Enviar mensagem"):
            if name and email and msg:
                st.success("Mensagem enviada! Retornaremos em breve. 🍫")
            else:
                st.error("Preencha todos os campos.")
