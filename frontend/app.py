import sys
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
from frontend.style import inject_css
from frontend.state import init_state, show_notification

import config

st.set_page_config(
    page_title="Alma de Cacau",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_state()


def _nav_item(label: str, page_key: str):
    """Renderiza item de nav ativo (HTML) ou botão clicável."""
    is_active = st.session_state.current_page == page_key
    if is_active:
        st.markdown(f'<div class="nav-active">{label}</div>', unsafe_allow_html=True)
    else:
        if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
            st.session_state.current_page = page_key
            st.rerun()


def sidebar_nav():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1.25rem 0 0.5rem;">
          <div style="font-family:'Playfair Display',serif;font-size:1.45rem;
                      color:#d4a96a;letter-spacing:2px;">🍫 Alma de Cacau</div>
          <div style="font-size:0.72rem;color:#8a6040;font-style:italic;
                      margin-top:5px;letter-spacing:0.5px;">
            Transformando chocolate em lembrança
          </div>
          <div style="height:1px;background:rgba(180,130,70,0.2);margin:14px 0 4px;"></div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.is_admin:
            st.markdown('<div style="font-size:0.68rem;color:#c8a070;letter-spacing:1.5px;'
                         'text-transform:uppercase;padding:6px 10px 2px;">Gestão</div>',
                         unsafe_allow_html=True)
            for label, key in [
                ("📊 Dashboard",    "admin_dashboard"),
                ("📦 Pedidos",      "admin_orders"),
                ("🍫 Produção",     "admin_production"),
                ("📋 Produtos",     "admin_products"),
            ]:
                _nav_item(label, key)

            st.markdown('<div style="font-size:0.68rem;color:#c8a070;letter-spacing:1.5px;'
                         'text-transform:uppercase;padding:10px 10px 2px;">Operações</div>',
                         unsafe_allow_html=True)
            for label, key in [
                ("🧑‍🤝‍🧑 Clientes",    "admin_customers"),
                ("🎫 Cupons",       "admin_coupons"),
                ("📦 Estoque",      "admin_inventory"),
                ("📈 Relatórios",   "admin_reports"),
            ]:
                _nav_item(label, key)
        else:
            from frontend.state import cart_count
            cart_n = cart_count()
            cart_label = f"🛒 Carrinho ({cart_n})" if cart_n else "🛒 Carrinho"

            # Assistente em destaque no topo
            st.markdown('<div style="font-size:0.66rem;color:#c8a070;letter-spacing:1.5px;'
                         'text-transform:uppercase;padding:6px 10px 2px;">Atendimento</div>',
                         unsafe_allow_html=True)
            _nav_item("🤖 Assistente IA", "assistant")

            st.markdown('<div style="font-size:0.66rem;color:#c8a070;letter-spacing:1.5px;'
                         'text-transform:uppercase;padding:8px 10px 2px;">Loja</div>',
                         unsafe_allow_html=True)
            for label, key in [
                ("🏠 Início",            "home"),
                ("🍫 Catálogo",           "catalog"),
                ("🎁 Presentes",          "gift"),
                ("🧩 Monte sua Caixa",    "build_box"),
                (cart_label,             "cart"),
            ]:
                _nav_item(label, key)

            st.markdown('<div style="font-size:0.66rem;color:#c8a070;letter-spacing:1.5px;'
                         'text-transform:uppercase;padding:8px 10px 2px;">Conta</div>',
                         unsafe_allow_html=True)
            for label, key in [
                ("📦 Rastrear Pedido",    "order_tracking"),
                ("👤 Minha Conta",        "my_account"),
            ]:
                _nav_item(label, key)

        st.markdown('<hr style="border:none;border-top:1px solid rgba(180,130,70,0.15);margin:12px 0 8px;">',
                     unsafe_allow_html=True)

        if st.session_state.user_id:
            first = st.session_state.customer_name.split()[0] if st.session_state.customer_name else "Cliente"
            st.markdown(
                f'<div style="font-size:0.78rem;color:#c8a070;padding:2px 10px 6px;">'
                f'Olá, <span style="color:#d4a96a;font-weight:600;">{first}</span> 🍫</div>',
                unsafe_allow_html=True,
            )
            if st.button("🚪 Sair", use_container_width=True, key="nav_logout"):
                for k in ["user_id", "customer_id", "customer_name", "is_admin"]:
                    st.session_state[k] = None if k != "is_admin" else False
                st.session_state.customer_name = ""
                st.rerun()
        else:
            if st.button("🔑 Entrar / Cadastrar", use_container_width=True, key="nav_login"):
                st.session_state.current_page = "my_account"
                st.rerun()


def render_page():
    page = st.session_state.current_page
    if st.session_state.is_admin:
        routes = {
            "admin_dashboard":  "frontend.pages.admin.dashboard",
            "admin_orders":     "frontend.pages.admin.orders",
            "admin_production": "frontend.pages.admin.production",
            "admin_products":   "frontend.pages.admin.products",
            "admin_customers":  "frontend.pages.admin.customers",
            "admin_coupons":    "frontend.pages.admin.coupons",
            "admin_inventory":  "frontend.pages.admin.inventory",
            "admin_reports":    "frontend.pages.admin.reports",
        }
        module = routes.get(page, "frontend.pages.admin.dashboard")
    else:
        routes = {
            "home":            "frontend.pages.customer.home",
            "catalog":         "frontend.pages.customer.catalog",
            "product_detail":  "frontend.pages.customer.product_detail",
            "build_box":       "frontend.pages.customer.build_box",
            "gift":            "frontend.pages.customer.gift",
            "cart":            "frontend.pages.customer.cart",
            "checkout":        "frontend.pages.customer.checkout",
            "order_tracking":  "frontend.pages.customer.order_tracking",
            "my_account":      "frontend.pages.customer.my_account",
            "assistant":       "frontend.pages.customer.assistant",
            "contact":         "frontend.pages.customer.contact",
        }
        module = routes.get(page, "frontend.pages.customer.home")

    import importlib
    mod = importlib.import_module(module)
    mod.render()


sidebar_nav()
show_notification()
render_page()


