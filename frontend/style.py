# ─────────────────────────────────────────────────────────────
# ALMA DE CACAU — Design System (Tema Claro Premium)
# ─────────────────────────────────────────────────────────────

ALMA_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lato:wght@300;400;600;700&display=swap');

/* ── TOKENS ───────────────────────────────────────── */
:root {
  /* Brand */
  --c-chocolate:   #5c2d0e;
  --c-caramel:     #c8953a;
  --c-gold:        #a07010;
  --c-gold-light:  #e8c060;
  --c-cream:       #fef8f0;

  /* Backgrounds – CLARO */
  --bg-app:        #fef8f0;
  --bg-surface:    #fff5e6;
  --bg-card:       #ffffff;
  --bg-card-hover: #fffaf3;
  --bg-input:      #fdf5e8;
  --bg-sidebar:    #1e0a02;
  --bg-sidebar-2:  #2a1003;

  /* Text */
  --tx-primary:    #2d1206;
  --tx-secondary:  #6b3a18;
  --tx-muted:      #9a7050;
  --tx-heading:    #5c2d0e;
  --tx-on-dark:    #f5e6d0;

  /* Border */
  --bd:            rgba(180, 130, 70, 0.22);
  --bd-hover:      rgba(160, 112, 16, 0.55);
  --bd-focus:      #a07010;
  --bd-card:       rgba(180, 130, 70, 0.18);

  /* Shadow */
  --sh-xs:   0 1px 4px  rgba(92,45,14,.06);
  --sh-sm:   0 2px 10px rgba(92,45,14,.09);
  --sh-md:   0 6px 24px rgba(92,45,14,.12);
  --sh-lg:   0 12px 40px rgba(92,45,14,.15);
  --sh-glow: 0 0 20px rgba(184,134,11,.25);

  /* Status */
  --s-success: #1a9550;
  --s-warning: #c87800;
  --s-error:   #c0392b;
  --s-info:    #1a6fa0;

  /* Spacing */
  --sp-xs:  4px;  --sp-sm:  8px;  --sp-md: 16px;
  --sp-lg: 24px;  --sp-xl: 36px;  --sp-2xl: 56px;

  /* Radius */
  --r-sm: 6px;  --r-md: 12px;  --r-lg: 18px;  --r-pill: 50px;

  /* Transition */
  --tr-fast: 0.15s ease;
  --tr-base: 0.25s ease;
  --tr-slow: 0.4s cubic-bezier(.4,0,.2,1);
}

/* ── KEYFRAMES ────────────────────────────────────── */
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
@keyframes shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(184,134,11,0); }
  50%       { box-shadow: 0 0 0 6px rgba(184,134,11,0.18); }
}

/* ── BASE ─────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
  background-color: var(--bg-app) !important;
  color: var(--tx-primary) !important;
  font-family: 'Lato', sans-serif;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-surface); }
::-webkit-scrollbar-thumb { background: var(--bd-hover); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--c-gold); }

/* ── TIPOGRAFIA ───────────────────────────────────── */
h1, h2, h3, h4 {
  font-family: 'Playfair Display', serif !important;
  color: var(--tx-heading) !important;
  letter-spacing: 0.3px;
}
h1 { font-size: 2rem !important; }
h2 { font-size: 1.5rem !important; }
h3 { font-size: 1.15rem !important; }
p  { color: var(--tx-secondary); line-height: 1.7; }

/* ── SIDEBAR ──────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #3b1f0c 0%, #2d1508 100%) !important;
  border-right: 1px solid rgba(212,169,106,0.2) !important;
}
[data-testid="stSidebar"] * {
  color: #e8c890 !important;
}
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: #d4a86a !important;
  border: none !important;
  border-radius: var(--r-sm) !important;
  font-size: 0.86rem !important;
  font-weight: 400 !important;
  padding: 0.42rem 0.85rem !important;
  text-align: left !important;
  transition: background var(--tr-fast), color var(--tr-fast) !important;
  box-shadow: none !important;
  letter-spacing: 0.2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(212,169,106,0.18) !important;
  color: #f5d898 !important;
  transform: none !important;
  box-shadow: none !important;
}

/* Nav ativo */
.nav-active {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0.42rem 0.85rem;
  background: rgba(212,169,106,0.22);
  border-left: 3px solid #d4a96a;
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  color: #f5d898 !important;
  font-size: 0.86rem;
  font-weight: 700;
  letter-spacing: 0.3px;
  margin: 1px 0;
}

/* ── BOTÕES (área principal) ──────────────────────── */
.main .stButton > button {
  background: linear-gradient(135deg, var(--c-chocolate) 0%, var(--c-gold) 100%) !important;
  color: #fef8f0 !important;
  border: none !important;
  border-radius: var(--r-md) !important;
  font-family: 'Lato', sans-serif !important;
  font-weight: 600 !important;
  letter-spacing: 0.6px !important;
  padding: 0.55rem 1.4rem !important;
  transition: all var(--tr-base) !important;
  box-shadow: var(--sh-sm) !important;
}
.main .stButton > button:hover {
  box-shadow: var(--sh-md) !important;
  transform: translateY(-2px) !important;
  filter: brightness(1.06) !important;
}
.main .stButton > button:active {
  transform: translateY(0) !important;
  box-shadow: var(--sh-xs) !important;
}
.main .stButton > button:focus-visible {
  outline: 2px solid var(--bd-focus) !important;
  outline-offset: 3px !important;
}

/* ── INPUTS ───────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  background-color: var(--bg-input) !important;
  color: var(--tx-primary) !important;
  border: 1.5px solid var(--bd) !important;
  border-radius: var(--r-md) !important;
  font-family: 'Lato', sans-serif !important;
  transition: border-color var(--tr-fast), box-shadow var(--tr-fast) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--bd-focus) !important;
  box-shadow: 0 0 0 3px rgba(160,112,16,0.12) !important;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
  background-color: var(--bg-input) !important;
  color: var(--tx-primary) !important;
  border: 1.5px solid var(--bd) !important;
  border-radius: var(--r-md) !important;
}
label {
  color: var(--tx-secondary) !important;
  font-size: 0.8rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.6px !important;
  text-transform: uppercase !important;
}

/* ── MÉTRICAS ─────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--bg-card) !important;
  border: 1.5px solid var(--bd-card) !important;
  border-radius: var(--r-lg) !important;
  padding: var(--sp-md) var(--sp-lg) !important;
  box-shadow: var(--sh-sm) !important;
  transition: all var(--tr-base) !important;
  animation: fadeSlideUp 0.35s ease !important;
}
[data-testid="stMetric"]:hover {
  border-color: var(--bd-hover) !important;
  box-shadow: var(--sh-md) !important;
  transform: translateY(-2px) !important;
}
[data-testid="stMetricValue"] {
  color: var(--c-chocolate) !important;
  font-family: 'Playfair Display', serif !important;
  font-size: 1.6rem !important;
}
[data-testid="stMetricLabel"] {
  color: var(--tx-muted) !important;
  font-size: 0.73rem !important;
  text-transform: uppercase !important;
  letter-spacing: 1px !important;
}

/* ── TABS ─────────────────────────────────────────── */
[data-testid="stTabs"] {
  background: var(--bg-card) !important;
  border-radius: var(--r-lg) !important;
  border: 1px solid var(--bd) !important;
  padding: var(--sp-sm) !important;
}
[data-testid="stTabs"] button {
  color: var(--tx-muted) !important;
  border-radius: var(--r-sm) var(--r-sm) 0 0 !important;
  transition: color var(--tr-fast) !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
  color: var(--c-chocolate) !important;
  border-bottom-color: var(--c-caramel) !important;
  font-weight: 700 !important;
}

/* ── EXPANDER ─────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--bg-card) !important;
  border: 1.5px solid var(--bd-card) !important;
  border-radius: var(--r-md) !important;
  box-shadow: var(--sh-xs) !important;
}

/* ── FORM ─────────────────────────────────────────── */
[data-testid="stForm"] {
  background: var(--bg-card) !important;
  border: 1.5px solid var(--bd-card) !important;
  border-radius: var(--r-lg) !important;
  padding: var(--sp-lg) !important;
  box-shadow: var(--sh-sm) !important;
}

/* ── CHAT ─────────────────────────────────────────── */
[data-testid="stChatMessage"] {
  animation: fadeSlideUp 0.3s ease;
  border-radius: var(--r-lg) !important;
  margin: 4px 0 !important;
}
[data-testid="stChatInput"] textarea {
  background: var(--bg-card) !important;
  border: 1.5px solid var(--bd) !important;
  border-radius: var(--r-lg) !important;
  color: var(--tx-primary) !important;
  transition: border-color var(--tr-fast), box-shadow var(--tr-fast) !important;
}
[data-testid="stChatInput"] textarea:focus {
  border-color: var(--bd-focus) !important;
  box-shadow: 0 0 0 3px rgba(160,112,16,0.1) !important;
}

/* ── ALERTS ───────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--r-md) !important;
  animation: fadeIn 0.3s ease !important;
}

/* ── DIVIDER ──────────────────────────────────────── */
hr { border-color: var(--bd) !important; margin: var(--sp-lg) 0 !important; }

/* ── CLASSES UTILITÁRIAS ──────────────────────────── */
.alma-card {
  background: var(--bg-card);
  border: 1.5px solid var(--bd-card);
  border-radius: var(--r-lg);
  padding: var(--sp-md);
  box-shadow: var(--sh-sm);
  transition: all var(--tr-slow);
  animation: fadeSlideUp 0.35s ease;
  position: relative;
  overflow: hidden;
}
.alma-card:hover {
  border-color: var(--bd-hover);
  box-shadow: var(--sh-md);
  transform: translateY(-3px);
}
.alma-card::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, transparent, var(--c-caramel), transparent);
  opacity: 0;
  transition: opacity var(--tr-base);
}
.alma-card:hover::after { opacity: 1; }

.alma-hero {
  background: linear-gradient(135deg, #fff5e0 0%, #fffaf0 50%, #fff8ec 100%);
  border: 1.5px solid rgba(180,130,70,0.2);
  border-radius: 20px;
  padding: 3rem 2.5rem;
  text-align: center;
  position: relative;
  overflow: hidden;
  box-shadow: var(--sh-sm);
  animation: fadeSlideUp 0.5s ease;
}
.alma-hero::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, transparent, var(--c-caramel), var(--c-gold), transparent);
}

.alma-section-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: var(--sp-xl) 0 var(--sp-lg);
  color: var(--tx-muted);
  font-size: 0.73rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  font-weight: 600;
}
.alma-section-divider::before,
.alma-section-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--bd));
}
.alma-section-divider::after {
  background: linear-gradient(90deg, var(--bd), transparent);
}

.hero-stat {
  background: var(--bg-card);
  border: 1.5px solid var(--bd-card);
  border-radius: var(--r-lg);
  padding: var(--sp-lg);
  text-align: center;
  box-shadow: var(--sh-sm);
  transition: all var(--tr-slow);
  animation: fadeSlideUp 0.4s ease;
}
.hero-stat:hover {
  border-color: var(--bd-hover);
  box-shadow: var(--sh-md);
  transform: translateY(-3px);
}
.hero-stat .stat-icon { font-size: 2rem; display: block; margin-bottom: 8px; }
.hero-stat .stat-title {
  color: var(--tx-heading);
  font-family: 'Playfair Display', serif;
  font-size: 1rem;
  font-weight: 700;
  margin: 4px 0;
}
.hero-stat .stat-desc { color: var(--tx-muted); font-size: 0.8rem; }

.price-tag {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--tx-heading);
  font-variant-numeric: tabular-nums;
}
.price-tag .currency {
  font-size: 0.85rem;
  color: var(--tx-muted);
  margin-right: 2px;
  font-weight: 400;
}

.stock-indicator { font-size: 0.73rem; display: inline-flex; align-items: center; gap: 5px; }
.stock-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.stock-ok  { background: var(--s-success); animation: pulse 2.5s infinite; }
.stock-low { background: var(--s-warning); }
.stock-out { background: var(--s-error); }

/* Chat bubbles customizados */
.chat-bubble-cta {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--bg-surface);
  border: 1.5px solid var(--bd);
  border-radius: var(--r-pill);
  padding: 6px 14px;
  font-size: 0.82rem;
  color: var(--tx-secondary);
  cursor: pointer;
  transition: all var(--tr-fast);
  text-decoration: none;
  font-family: 'Lato', sans-serif;
}
.chat-bubble-cta:hover {
  background: var(--bg-card);
  border-color: var(--c-gold);
  color: var(--c-chocolate);
  box-shadow: var(--sh-xs);
}

.notification-bar {
  border-radius: var(--r-md);
  padding: 10px 16px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: fadeSlideUp 0.3s ease;
}
</style>
"""


# ──────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────

def inject_css():
    """Injeta o design system via st.markdown (st.html usa iframe e não afeta a página)."""
    import streamlit as st
    st.markdown(ALMA_CSS, unsafe_allow_html=True)


def product_card_html(product: dict) -> str:
    allergens_html = ""
    if product.get("allergens"):
        badges = "".join(
            f'<span style="background:rgba(180,130,70,0.12);color:#6b3a18;'
            f'padding:2px 9px;border-radius:50px;font-size:10px;'
            f'margin:2px 2px 0 0;display:inline-block;border:1px solid rgba(180,130,70,0.2);">'
            f'{a.get("icon") or "?"} {a["name"]}</span>'
            for a in product["allergens"]
        )
        allergens_html = f'<div style="margin-top:10px;display:flex;flex-wrap:wrap;">{badges}</div>'

    tags = []
    if product.get("is_featured"):
        tags.append('<span style="background:#fff3cd;color:#856404;font-size:10px;'
                    'padding:2px 8px;border-radius:50px;font-weight:600;">* DESTAQUE</span>')
    if product.get("is_best_seller"):
        tags.append('<span style="background:#ffe5cc;color:#7a3e0a;font-size:10px;'
                    'padding:2px 8px;border-radius:50px;font-weight:600;">TOP VENDA</span>')
    if product.get("is_seasonal"):
        tags.append('<span style="background:#e8f5e9;color:#1a6b3a;font-size:10px;'
                    'padding:2px 8px;border-radius:50px;font-weight:600;">SAZONAL</span>')
    tags_html = (
        f'<div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:8px;">{"".join(tags)}</div>'
        if tags else ""
    )

    qty = product.get("available_quantity", 0)
    if qty == 0:
        dot, stock_label, sc = "stock-out", "Indisponivel", "#c0392b"
    elif qty <= 5:
        dot, stock_label, sc = "stock-low", f"{qty} restantes", "#c87800"
    else:
        dot, stock_label, sc = "stock-ok", f"{qty} disponiveis", "#1a9550"

    flavor_line = product.get("flavor_tagline") or product.get("flavor_name") or ""

    return (
        f'<div class="alma-card" style="min-height:155px;">'
        f'{tags_html}'
        f'<div style="font-family:Playfair Display,serif;font-size:1.05rem;'
        f'color:#5c2d0e;margin-bottom:2px;line-height:1.3;font-weight:700;">{product["name"]}</div>'
        + (f'<div style="font-size:0.78rem;color:#9a7050;font-style:italic;margin-bottom:10px;">'
           f'{flavor_line}</div>' if flavor_line else '')
        + f'<div style="display:flex;justify-content:space-between;align-items:center;'
          f'margin-top:8px;padding-top:8px;border-top:1px solid rgba(180,130,70,0.12);">'
          f'<div class="price-tag"><span class="currency">R$</span>{product.get("price",0):.2f}</div>'
          f'<span class="stock-indicator">'
          f'<span class="stock-dot {dot}"></span>'
          f'<span style="color:{sc};font-size:0.72rem;font-weight:600;">{stock_label}</span>'
          f'</span></div>'
          f'{allergens_html}'
          f'</div>'
    )


def section_header(title: str, subtitle: str = "") -> str:
    sub = (
        f'<p style="color:#9a7050;font-size:0.95rem;margin-top:6px;font-style:italic;">{subtitle}</p>'
        if subtitle else ""
    )
    return (
        f'<div style="text-align:center;padding:1.75rem 0 1rem;">'
        f'<h1 style="font-family:Playfair Display,serif;color:#5c2d0e;'
        f'font-size:1.9rem;letter-spacing:0.8px;margin-bottom:0;">{title}</h1>'
        f'{sub}'
        f'<div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-top:12px;">'
        f'<div style="width:36px;height:1px;background:rgba(180,130,70,0.35);"></div>'
        f'<div style="width:5px;height:5px;border-radius:50%;background:#a07010;"></div>'
        f'<div style="width:36px;height:1px;background:rgba(180,130,70,0.35);"></div>'
        f'</div></div>'
    )


def section_label(text: str) -> str:
    return f'<div class="alma-section-divider">{text}</div>'


def status_badge(status: str) -> str:
    cfg = {
        "pending":       ("Pendente",     "#fff3cd", "#856404"),
        "confirmed":     ("Confirmado",   "#d4edda", "#155724"),
        "in_production": ("Em Producao",  "#ffecd2", "#7a3e0a"),
        "ready":         ("Pronto",       "#d4edda", "#155724"),
        "shipped":       ("Enviado",      "#cce5ff", "#004085"),
        "delivered":     ("Entregue",     "#d4edda", "#155724"),
        "cancelled":     ("Cancelado",    "#f8d7da", "#721c24"),
    }
    label, bg, fg = cfg.get(status, (status, "#e2e3e5", "#383d41"))
    return (
        f'<span style="background:{bg};color:{fg};padding:4px 14px;'
        f'border-radius:50px;font-size:0.75rem;font-weight:700;">'
        f'{label}</span>'
    )


def hero_stat_card(icon: str, title: str, desc: str) -> str:
    return (
        f'<div class="hero-stat">'
        f'<span class="stat-icon">{icon}</span>'
        f'<div class="stat-title">{title}</div>'
        f'<div class="stat-desc">{desc}</div>'
        f'</div>'
    )

