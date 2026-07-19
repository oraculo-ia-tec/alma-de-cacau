import streamlit as st
from typing import List

STATUS_LABELS = {
    "pending": ("⏳", "Pendente", "#ffcc44"),
    "confirmed": ("✅", "Confirmado", "#66bbff"),
    "in_production": ("🍫", "Em Producao", "#ff9944"),
    "ready": ("📦", "Pronto", "#88ff88"),
    "shipped": ("🚚", "Enviado", "#aaaaff"),
    "delivered": ("🎉", "Entregue", "#44dd88"),
    "cancelled": ("❌", "Cancelado", "#ff6666"),
}


def order_timeline(history: List[dict]):
    if not history:
        st.info("Sem historico de status.")
        return
    for h in history:
        status = h.get("to", "")
        icon, label, color = STATUS_LABELS.get(status, ("🔵", status, "#aaaaaa"))
        at = h.get("at", "")[:16].replace("T", " ")
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px;margin:8px 0;'
            f'padding:10px 16px;background:rgba(60,30,10,0.4);border-radius:8px;'
            f'border-left:3px solid {color};">'
            f'<span style="font-size:20px;">{icon}</span>'
            f'<div><div style="color:{color};font-weight:600;">{label}</div>'
            f'<div style="color:#a0836a;font-size:11px;">{at}</div></div></div>',
            unsafe_allow_html=True,
        )
