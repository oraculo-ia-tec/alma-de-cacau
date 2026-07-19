import streamlit as st
from frontend.style import section_header, section_label, hero_stat_card
from frontend.mcp_client import get_products
from frontend.components.product_card import product_card


def _product_row(products: list, key_prefix: str):
    if not products:
        st.info("Nenhum produto disponível no momento.")
        return
    cols = st.columns(min(len(products), 4))
    for col, p in zip(cols, products):
        with col:
            product_card(p, key_prefix=key_prefix)


def render():
    # ── Hero ──────────────────────────────────────────
    st.html("""
    <div style="
        background: linear-gradient(135deg, #1e0d04 0%, #2a1003 50%, #3b1f0c 100%);
        border: 1px solid rgba(180,130,70,0.2);
        border-radius: 18px;
        padding: 3rem 2.5rem;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    ">
      <div style="position:absolute;top:0;left:0;right:0;height:2px;
                  background:linear-gradient(90deg,transparent,#b8860b,transparent);"></div>
      <div style="font-family:'Playfair Display',serif;font-size:0.8rem;
                  color:#8a6040;letter-spacing:3px;text-transform:uppercase;margin-bottom:12px;">
        Chocolates Artesanais
      </div>
      <h1 style="font-family:'Playfair Display',serif;color:#d4a96a;
                 font-size:2.4rem;margin:0;letter-spacing:1px;line-height:1.25;">
        Alma de Cacau
      </h1>
      <p style="color:#8a6040;font-style:italic;margin:12px 0 0;font-size:1rem;line-height:1.6;">
        Transformando chocolate em lembrança — feito à mão, com carinho.
      </p>
    </div>
    """)

    # ── CTAs ──────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.html(hero_stat_card("🎁", "Caixas Presente", "Monte sua caixa personalizada"))
        if st.button("Montar Caixa", use_container_width=True, key="home_gift"):
            st.session_state.current_page = "build_box"
            st.rerun()
    with c2:
        st.html(hero_stat_card("🤖", "Assistente IA", "Recomendações personalizadas"))
        if st.button("Falar com Assistente", use_container_width=True, key="home_ai"):
            st.session_state.current_page = "assistant"
            st.rerun()
    with c3:
        st.html(hero_stat_card("🍫", "Ver Catálogo", "Todos os nossos sabores"))
        if st.button("Ver Catálogo", use_container_width=True, key="home_cat"):
            st.session_state.current_page = "catalog"
            st.rerun()

    # ── Destaques ─────────────────────────────────────
    st.html('<div class="alma-section-divider">⭐ Destaques da Casa</div>')
    _product_row(get_products(only_featured=True, page_size=4), "feat")

    # ── Mais Vendidos ─────────────────────────────────
    st.html('<div class="alma-section-divider">🔥 Mais Vendidos</div>')
    _product_row(get_products(only_best_sellers=True, page_size=4), "best")


    st.markdown("### ⭐ Destaques da Casa")
    featured = get_products(only_featured=True, page_size=4)
    if featured:
        cols = st.columns(min(len(featured), 4))
        for col, p in zip(cols, featured):
            with col:
                product_card(p, key_prefix="feat")
    else:
        st.info("Nenhum produto em destaque no momento.")

    st.divider()
    st.markdown("### 🔥 Mais Vendidos")
    best = get_products(only_best_sellers=True, page_size=4)
    if best:
        cols = st.columns(min(len(best), 4))
        for col, p in zip(cols, best):
            with col:
                product_card(p, key_prefix="best")

    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div style='text-align:center;padding:1.5rem;background:rgba(60,30,10,0.4);
                    border-radius:12px;border:1px solid rgba(180,130,70,0.2);'>
            <div style='font-size:2rem;'>🎁</div>
            <div style='color:#d4a96a;font-family:Playfair Display,serif;margin:8px 0;'>Caixas Presente</div>
            <div style='color:#a0836a;font-size:13px;'>Monte sua caixa personalizada</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Montar Caixa", use_container_width=True, key="home_gift"):
            st.session_state.current_page = "build_box"
            st.rerun()
    with c2:
        st.markdown("""
        <div style='text-align:center;padding:1.5rem;background:rgba(60,30,10,0.4);
                    border-radius:12px;border:1px solid rgba(180,130,70,0.2);'>
            <div style='font-size:2rem;'>🤖</div>
            <div style='color:#d4a96a;font-family:Playfair Display,serif;margin:8px 0;'>Assistente IA</div>
            <div style='color:#a0836a;font-size:13px;'>Recomendacoes personalizadas</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Falar com Assistente", use_container_width=True, key="home_ai"):
            st.session_state.current_page = "assistant"
            st.rerun()
    with c3:
        st.markdown("""
        <div style='text-align:center;padding:1.5rem;background:rgba(60,30,10,0.4);
                    border-radius:12px;border:1px solid rgba(180,130,70,0.2);'>
            <div style='font-size:2rem;'>🔍</div>
            <div style='color:#d4a96a;font-family:Playfair Display,serif;margin:8px 0;'>Ver Catalogo</div>
            <div style='color:#a0836a;font-size:13px;'>Todos os nossos sabores</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Catalogo", use_container_width=True, key="home_cat"):
            st.session_state.current_page = "catalog"
            st.rerun()
