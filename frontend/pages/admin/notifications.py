import streamlit as st
from frontend.style import section_header
from database.engine import get_db
from database.models import NotificationLog
from sqlalchemy import desc


def render():
    st.markdown(section_header("📨 Notificacoes"), unsafe_allow_html=True)
    with get_db() as db:
        logs = db.query(NotificationLog).order_by(desc(NotificationLog.created_at)).limit(50).all()
    if not logs:
        st.info("Nenhuma notificacao registrada.")
        return
    for log in logs:
        icon = "✅" if log.was_sent else "❌"
        st.markdown(
            f"{icon} `{log.channel.value}` — **{log.subject or 'sem assunto'}** — "
            f"{log.created_at.strftime('%d/%m/%Y %H:%M')}"
        )
        if log.error_message:
            st.caption(f"Erro: {log.error_message}")
