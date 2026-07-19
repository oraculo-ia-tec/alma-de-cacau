import streamlit as st
from typing import List, Optional


def flavor_selector(flavors: List[str], key: str = "flavor") -> Optional[str]:
    options = ["Todos os sabores"] + flavors
    selected = st.selectbox("🍫 Filtrar por sabor", options, key=key)
    return None if selected == "Todos os sabores" else selected
