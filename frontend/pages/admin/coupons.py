import streamlit as st
from frontend.style import section_header
from database.engine import get_db
from database.models import Coupon
from datetime import date
from decimal import Decimal


def render():
    st.markdown(section_header("🎫 Cupons de Desconto"), unsafe_allow_html=True)

    with get_db() as db:
        coupons = db.query(Coupon).order_by(Coupon.valid_until.desc()).all()

    with st.expander("➕ Criar novo cupom"):
        with st.form("new_coupon"):
            code = st.text_input("Codigo").upper()
            desc = st.text_input("Descricao")
            disc_type = st.radio("Tipo", ["Percentual (%)", "Valor fixo (R$)"], horizontal=True)
            disc_val = st.number_input("Valor do desconto", min_value=0.0, step=0.5)
            min_order = st.number_input("Pedido minimo (R$)", min_value=0.0)
            max_uses = st.number_input("Usos maximos (0 = ilimitado)", min_value=0, step=1)
            valid_from = st.date_input("Valido de", value=date.today())
            valid_until = st.date_input("Valido ate")
            if st.form_submit_button("Criar Cupom"):
                with get_db() as db2:
                    c = Coupon(
                        code=code, description=desc,
                        discount_percent=Decimal(str(disc_val)) if "Percentual" in disc_type else None,
                        discount_fixed=Decimal(str(disc_val)) if "fixo" in disc_type else None,
                        min_order_value=Decimal(str(min_order)),
                        max_uses=max_uses or None,
                        valid_from=valid_from, valid_until=valid_until,
                    )
                    db2.add(c)
                st.success(f"Cupom '{code}' criado!")
                st.rerun()

    st.markdown("### Cupons Cadastrados")
    for c in coupons:
        status = "✅" if c.is_active and c.valid_until >= date.today() else "❌"
        st.markdown(
            f"{status} **{c.code}** — {c.description or ''} — "
            f"Valido ate {c.valid_until} — Usos: {c.used_count}/{c.max_uses or 'inf'}"
        )
