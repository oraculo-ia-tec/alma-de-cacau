import streamlit as st
from typing import List


def allergen_badges(allergens: List[dict]):
    if not allergens:
        st.markdown(
            '<span style="color:#90ee90;font-size:12px;">Sem alergênicos declarados</span>',
            unsafe_allow_html=True,
        )
        return
    badges_html = ""
    for a in allergens:
        color = "rgba(255,150,0,0.2)" if a.get("is_trace") else "rgba(200,50,50,0.2)"
        text_color = "#ffaa00" if a.get("is_trace") else "#ff9999"
        icon = a.get("icon") or "⚠️"
        label = f"Pode conter: {a['name']}" if a.get("is_trace") else a["name"]
        badges_html += (
            f'<span style="background:{color};color:{text_color};padding:3px 10px;'
            f'border-radius:20px;font-size:11px;margin:2px;display:inline-block;">'
            f'{icon} {label}</span>'
        )
    st.markdown(f'<div style="margin:4px 0;">{badges_html}</div>', unsafe_allow_html=True)
