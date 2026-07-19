import streamlit as st
from typing import List


def gift_builder_summary(items: List[dict], packaging_type: str = "standard"):
    if not items:
        st.info("Nenhum item adicionado.")
        return
    packaging_prices = {"standard": 5.0, "premium": 12.0, "luxury": 25.0}
    total = sum(i["price"] * i["quantity"] for i in items)
    total += packaging_prices.get(packaging_type, 5.0)
    st.markdown("#### 🎁 Resumo da Caixa")
    for item in items:
        st.markdown(f"- {item['name']} x{item['quantity']} — R$ {item['price'] * item['quantity']:.2f}")
    st.markdown(f"- Embalagem **{packaging_type}**: R$ {packaging_prices.get(packaging_type, 5.0):.2f}")
    st.markdown(f"**Total: R$ {total:.2f}**")
