"""
Assistente Cacau - Landing Page da Alma de Cacau
Com deteccao de produto e exibicao de imagem automatica
"""
import os
import re
import base64
from pathlib import Path

import streamlit as st
from groq import Groq

import config

GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL     = "llama-3.3-70b-versatile"

_LOGO_PATH     = Path(__file__).parents[3] / "logomarca.jpg"
_PRODUCTS_DIR  = Path(__file__).parents[3] / "produtos"

# --- Catalogo de produtos com imagens ---
_PRODUCT_MAP = {
    "amarula":           {"file": "amarula.png",                    "label": "Trufa de Amarula",                "price": "R$ 9,90"},
    "cafe":              {"file": "cafe.png",                       "label": "Trufa de Cafe",                   "price": "R$ 8,90"},
    "castanha":          {"file": "castanha.png",                   "label": "Trufa de Castanha",               "price": "R$ 9,50"},
    "chocolate branco":  {"file": "chocolate-branco.png",           "label": "Trufa de Chocolate Branco",       "price": "R$ 9,50"},
    "doce de leite":     {"file": "doce-de-leite-com-amendoim.png", "label": "Trufa Doce de Leite c/ Amendoim", "price": "R$ 9,90"},
    "amendoim":          {"file": "doce-de-leite-com-amendoim.png", "label": "Trufa Doce de Leite c/ Amendoim", "price": "R$ 9,90"},
    "pimenta":           {"file": "pimenta.png",                    "label": "Trufa de Pimenta",                "price": "R$ 10,50"},
    "pistache":          {"file": "pistache.png",                   "label": "Trufa de Pistache",               "price": "R$ 10,50"},
}

_WELCOME = (
    "Ola! Seja muito bem-vindo(a) a **Alma de Cacau**!\n\n"
    "Sou a **Cacau**, sua assistente pessoal de chocolates artesanais. "
    "Estou aqui para ajuda-lo(a) a encontrar o bombom perfeito para cada momento especial.\n\n"
    "Como posso te chamar?"
)

_SYSTEM_PROMPT = """Voce e a Cacau, assistente virtual da Alma de Cacau - marca artesanal premium de trufas e bombons feitos a mao.

Objetivo: FAZER A VENDA com carinho e naturalidade.

Fluxo:
1. Descobrir o nome do cliente
2. Entender a ocasiao (presente, consumo proprio, evento, data especial)
3. Perguntar sobre restricoes alimentares
4. Recomendar produtos com descricao sensorial e emocional
5. Apresentar precos com naturalidade
6. Coletar: nome completo, WhatsApp e e-mail para o pedido
7. Orientar para finalizar pelo menu lateral (Catalogo ou Monte sua Caixa)

CATALOGO COMPLETO - Trufas Artesanais (unidade):
- Trufa de Amarula - R$ 9,90 | cremosa, com notas de baunilha e licor exotico
- Trufa de Cafe - R$ 8,90 | intense, para os amantes de cafe com chocolate
- Trufa de Castanha - R$ 9,50 | crocante, com castanha selecionada envolta em chocolate
- Trufa de Chocolate Branco - R$ 9,50 | delicada e doce, suave ao paladar
- Trufa Doce de Leite com Amendoim - R$ 9,90 | brasileira, cremosa com crocancia
- Trufa de Pimenta - R$ 10,50 | ousada, combinacao inusitada e marcante
- Trufa de Pistache - R$ 10,50 | sofisticada, sabor premium muito procurado

Caixas e Embalagens:
- Caixa Degustacao 9 unidades - R$ 69,90 | mix a escolher
- Embalagem Standard - R$ 5,00 | Embalagem Premium - R$ 12,00 | Embalagem Luxury - R$ 25,00

Regras IMPORTANTES:
- Use EXATAMENTE os nomes dos produtos acima para que as fotos aparecam automaticamente
- Nunca invente produtos ou precos alem dos listados
- Confirme alergicos: amendoim, castanha, laticinios quando relevante
- Seja breve: no maximo 2 perguntas por mensagem
- Tom: afetuoso, elegante, artesanal, sensorial, proximo
- Quando mencionar um produto, descreva sua experiencia sensorial
"""


def _logo_html() -> str:
    if _LOGO_PATH.exists():
        data = base64.b64encode(_LOGO_PATH.read_bytes()).decode()
        return (
            '<div style="display:flex;justify-content:center;margin:0.5rem 0 1rem;">'
            f'<img src="data:image/jpeg;base64,{data}" '
            'style="width:200px;height:200px;border-radius:50%;object-fit:cover;'
            'box-shadow:0 6px 28px rgba(92,45,14,0.28),'
            '0 0 0 4px rgba(212,169,106,0.35),'
            '0 0 0 8px rgba(212,169,106,0.12);">'
            '</div>'
        )
    return '<div style="text-align:center;font-size:3.5rem;margin:1rem 0;">ðŸ«</div>'


def _detect_products(text: str) -> list:
    """Detecta produtos mencionados no texto e retorna lista de dicts com path."""
    text_lower = text.lower()
    found = []
    seen_files = set()
    for keyword, prod in _PRODUCT_MAP.items():
        if keyword in text_lower and prod["file"] not in seen_files:
            img_path = _PRODUCTS_DIR / prod["file"]
            if img_path.exists():
                found.append({**prod, "path": str(img_path)})
                seen_files.add(prod["file"])
    return found


def _show_product_images(products: list) -> None:
    """Exibe imagens dos produtos detectados em colunas com label e preco."""
    if not products:
        return
    n = min(len(products), 4)
    cols = st.columns(n)
    for col, p in zip(cols, products[:4]):
        with col:
            st.image(p["path"], use_container_width=True)
            st.caption(f"**{p['label']}**  \n{p['price']}")


def _init_state() -> None:
    defaults = {
        "messages":     [],
        "lead_name":    "",
        "lead_phone":   "",
        "lead_email":   "",
        "chat_started": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _call_groq() -> str:
    if not GROQ_API_KEY:
        return "GROQ_API_KEY nao configurada no .env"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        payload = [{"role": "system", "content": _SYSTEM_PROMPT}]
        payload += [{"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages]
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=payload,
            temperature=0.3,
            max_tokens=500,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao conectar com a IA: {e}"


def _extract_lead(text: str) -> None:
    lower = text.lower()
    for t in ["me chamo", "meu nome e", "sou o ", "sou a ", "pode me chamar de"]:
        if t in lower:
            part = text.split(t, 1)[-1].strip().split()[0].capitalize()
            if part and not st.session_state.lead_name:
                st.session_state.lead_name = part
    phones = re.findall(r"\d{10,11}", re.sub(r"\D", "", text))
    if phones and not st.session_state.lead_phone:
        st.session_state.lead_phone = phones[0]
    emails = re.findall(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
    if emails and not st.session_state.lead_email:
        st.session_state.lead_email = emails[0].lower()


def render():
    _init_state()

    # Logomarca centralizada
    st.markdown(_logo_html(), unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:#9a7050;font-style:italic;'
        'margin:-6px 0 1.5rem;font-size:0.9rem;">'
        'Atendimento personalizado &nbsp;Â·&nbsp; Trufas artesanais feitas a mao</p>',
        unsafe_allow_html=True,
    )

    # Boas-vindas na primeira abertura
    if not st.session_state.chat_started:
        st.session_state.messages.append({"role": "assistant", "content": _WELCOME})
        st.session_state.chat_started = True

    # Historico de mensagens com exibicao de imagens
    for msg in st.session_state.messages:
        avatar = ":material/smart_toy:" if msg["role"] == "assistant" else ":material/person:"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                products = _detect_products(msg["content"])
                _show_product_images(products)

    # Input do chat
    if prompt := st.chat_input("Digite sua mensagem para a Cacau..."):
        _extract_lead(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            with st.spinner(""):
                response = _call_groq()
            st.markdown(response)
            products = _detect_products(response)
            _show_product_images(products)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Rodape
    st.divider()
    if st.button("ðŸ—‘ï¸ Limpar conversa", key="clr_chat"):
        for k in ["messages", "lead_name", "lead_phone", "lead_email", "chat_started"]:
            st.session_state.pop(k, None)
        st.rerun()
