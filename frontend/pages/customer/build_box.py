import streamlit as st
from frontend.style import section_header
from frontend.mcp_client import get_products
from frontend.state import set_notification
from database.engine import get_db
from services.gift_service import GiftService
from schemas.gift import CreateGiftBoxInput, GiftBoxItemInput, PersonalizedCardInput
from database.models import OccasionType
from typing import Optional


def render():
    st.markdown(section_header("🧩 Monte sua Caixa",
                               "Escolha os produtos e personalize o presente"),
                unsafe_allow_html=True)

    products = get_products(page_size=50)
    if not products:
        st.info("Nenhum produto disponivel.")
        return

    product_map = {p["name"]: p for p in products}
    selected_names = st.multiselect(
        "🍫 Escolha os produtos",
        list(product_map.keys()),
        max_selections=12,
    )

    if not selected_names:
        st.info("Selecione pelo menos 1 produto para montar a caixa.")
        return

    items_inputs = []
    total = 0.0
    for name in selected_names:
        p = product_map[name]
        qty = st.number_input(f"Qtd de '{name}'", min_value=1, max_value=10, value=1, key=f"qty_{p['id']}")
        items_inputs.append({"product_id": p["id"], "quantity": qty})
        total += p["price"] * qty

    packaging = st.selectbox("Embalagem", ["standard (R$ 5,00)", "premium (R$ 12,00)", "luxury (R$ 25,00)"])
    packaging_type = packaging.split()[0]
    packaging_prices = {"standard": 5.0, "premium": 12.0, "luxury": 25.0}
    total += packaging_prices.get(packaging_type, 5.0)

    st.markdown(f"**Total estimado: R$ {total:.2f}**")

    with st.expander("💌 Adicionar cartao personalizado (opcional)"):
        sender = st.text_input("De quem e o presente?")
        recipient = st.text_input("Para quem?")
        occasion = st.selectbox("Ocasiao", [o.value for o in OccasionType])
        message = st.text_area("Mensagem")

    box_name = st.text_input("Nome da caixa", value="Minha Caixa Especial")

    if st.button("🎁 Criar Caixa de Presente", use_container_width=True, type="primary"):
        card = None
        if sender and recipient and message:
            card = PersonalizedCardInput(
                sender_name=sender, recipient_name=recipient,
                message=message, occasion=OccasionType(occasion),
            )
        data = CreateGiftBoxInput(
            name=box_name,
            items=[GiftBoxItemInput(**i) for i in items_inputs],
            packaging_type=packaging_type,
            occasion=OccasionType(occasion) if card else None,
            card=card,
        )
        with get_db() as db:
            svc = GiftService(db)
            gift_box, err = svc.create_gift_box(data)
            if err:
                st.error(err)
            else:
                price, _ = svc.calculate_price(gift_box.id)
                set_notification(f"Caixa '{box_name}' criada! Total: R$ {float(price):.2f} 🎁")
                st.success(f"Caixa criada com sucesso! ID: {gift_box.id}")
