import streamlit as st
from typing import Optional


def init_state():
    defaults = {
        "cart": [],
        "user_id": None,
        "customer_id": None,
        "customer_name": "",
        "customer_email": "",
        "is_admin": False,
        "current_page": "assistant",   # landing page = assistente
        "selected_product_id": None,
        "gift_box_items": [],
        "last_order_number": None,
        "notification": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def cart_add(product_id: int, name: str, price: float, quantity: int = 1):
    for item in st.session_state.cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            return
    st.session_state.cart.append({
        "product_id": product_id, "name": name,
        "price": price, "quantity": quantity,
    })


def cart_remove(product_id: int):
    st.session_state.cart = [
        i for i in st.session_state.cart if i["product_id"] != product_id
    ]


def cart_clear():
    st.session_state.cart = []


def cart_total() -> float:
    return sum(i["price"] * i["quantity"] for i in st.session_state.cart)


def cart_count() -> int:
    return sum(i["quantity"] for i in st.session_state.cart)


def set_notification(msg: str, ntype: str = "success"):
    st.session_state.notification = {"type": ntype, "msg": msg}


def show_notification():
    n = st.session_state.get("notification")
    if n:
        icon = "✅" if n["type"] == "success" else "⚠️" if n["type"] == "warning" else "❌"
        bg   = "rgba(68,221,136,0.12)" if n["type"] == "success" else \
               "rgba(255,204,68,0.12)" if n["type"] == "warning" else \
               "rgba(255,107,107,0.12)"
        border = "#44dd88" if n["type"] == "success" else \
                 "#ffcc44" if n["type"] == "warning" else "#ff6b6b"
        text   = "#44dd88" if n["type"] == "success" else \
                 "#ffcc44" if n["type"] == "warning" else "#ff6b6b"
        st.html(f"""
        <div style="background:{bg};border:1px solid {border};border-radius:10px;
                    padding:10px 16px;margin-bottom:12px;display:flex;
                    align-items:center;gap:10px;">
          <span style="font-size:1.1rem;">{icon}</span>
          <span style="color:{text};font-size:0.88rem;font-weight:600;">{n['msg']}</span>
        </div>
        """)
        st.session_state.notification = None

