"""
Assistente Cacau - Landing Page da Alma de Cacau
Atendimento guiado: nome -> preferência de sabor -> compra.
"""

import base64
import os
import re
from pathlib import Path

import streamlit as st
from groq import Groq

import config  # Mantido para validar as configurações obrigatórias do projeto.


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

_LOGO_PATH = Path(__file__).parents[3] / "logomarca.jpg"
_PRODUCTS_DIR = Path(__file__).parents[3] / "produtos"


# --- Catálogo de produtos com imagens ---
_PRODUCT_MAP = {
    "amarula": {
        "file": "amarula.png",
        "label": "Trufa de Amarula",
        "price": "R$ 9,90",
    },
    "café": {
        "file": "cafe.png",
        "label": "Trufa de Café",
        "price": "R$ 8,90",
    },
    "cafe": {
        "file": "cafe.png",
        "label": "Trufa de Café",
        "price": "R$ 8,90",
    },
    "castanha": {
        "file": "castanha.png",
        "label": "Trufa de Castanha",
        "price": "R$ 9,50",
    },
    "chocolate branco": {
        "file": "chocolate-branco.png",
        "label": "Trufa de Chocolate Branco",
        "price": "R$ 9,50",
    },
    "doce de leite": {
        "file": "doce-de-leite-com-amendoim.png",
        "label": "Trufa Doce de Leite com Amendoim",
        "price": "R$ 9,90",
    },
    "amendoim": {
        "file": "doce-de-leite-com-amendoim.png",
        "label": "Trufa Doce de Leite com Amendoim",
        "price": "R$ 9,90",
    },
    "pimenta": {
        "file": "pimenta.png",
        "label": "Trufa de Pimenta",
        "price": "R$ 10,50",
    },
    "pistache": {
        "file": "pistache.png",
        "label": "Trufa de Pistache",
        "price": "R$ 10,50",
    },
}


_WELCOME = (
    "Olá! Seja muito bem-vindo(a) à **Alma de Cacau**! 🍫\n\n"
    "Sou a **Cacau**, sua assistente de chocolates artesanais. "
    "Antes de te apresentar nossos bombons, como posso te chamar?"
)


_SYSTEM_PROMPT = """
Você é a Cacau, assistente virtual da Alma de Cacau, marca premium de
trufas e bombons artesanais feitos à mão.

CONTEXTO FIXO:
- Todo visitante que chega a este chat deseja comprar bombons artesanais.
- O nome do cliente já foi coletado antes da sua resposta.
- A primeira pergunta após saber o nome é sempre sobre preferência de sabor.

FLUXO OBRIGATÓRIO:
1. Se o cliente acabou de informar o nome, trate-o amigavelmente pelo nome
   uma única vez e pergunte: "Você já tem algum sabor em mente ou prefere
   que eu apresente os sabores disponíveis?"
2. Não pergunte sobre presente, evento, ocasião ou data especial antes de
   o cliente mencionar esse assunto.
3. Se o cliente quiser conhecer os sabores, apresente as opções de modo breve,
   organizado e com os respectivos preços.
4. Depois de identificar os sabores, ajude com quantidade, caixa, embalagem
   e, quando apropriado, retirada ou entrega.
5. Pergunte sobre alergias somente quando houver recomendação ou compra que
   envolva amendoim, castanha ou laticínios.
6. Não peça o nome novamente e não repita o nome em toda resposta.
7. Faça no máximo uma pergunta por resposta.
8. Não invente produtos, preços, promoções, estoque ou prazos.

CATÁLOGO — Trufas artesanais por unidade:
- Trufa de Amarula — R$ 9,90 | cremosa, com notas de baunilha e licor exótico.
- Trufa de Café — R$ 8,90 | intensa, para amantes de café com chocolate.
- Trufa de Castanha — R$ 9,50 | crocante, com castanha selecionada envolta em chocolate.
- Trufa de Chocolate Branco — R$ 9,50 | delicada, doce e suave ao paladar.
- Trufa Doce de Leite com Amendoim — R$ 9,90 | cremosa, brasileira e crocante.
- Trufa de Pimenta — R$ 10,50 | ousada, marcante e levemente picante.
- Trufa de Pistache — R$ 10,50 | sofisticada e premium.

Caixas e embalagens:
- Caixa Degustação, 9 unidades — R$ 69,90 | mix à escolha.
- Embalagem Standard — R$ 5,00.
- Embalagem Premium — R$ 12,00.
- Embalagem Luxury — R$ 25,00.

REGRAS:
- Use exatamente os nomes dos produtos do catálogo ao recomendá-los.
- Tom: acolhedor, elegante, breve, natural e voltado à venda.
- Ao mencionar um sabor, descreva a experiência sensorial de forma breve.
"""


def _logo_html() -> str:
    """Retorna a logomarca em HTML; usa ícone de chocolate como fallback."""
    if _LOGO_PATH.exists():
        data = base64.b64encode(_LOGO_PATH.read_bytes()).decode()
        return (
            '<div style="display:flex;justify-content:center;margin:0.5rem 0 1rem;">'
            f'<img src="data:image/jpeg;base64,{data}" '
            'style="width:200px;height:200px;border-radius:50%;object-fit:cover;'
            'box-shadow:0 6px 28px rgba(92,45,14,0.28),'
            '0 0 0 4px rgba(212,169,106,0.35),'
            '0 0 0 8px rgba(212,169,106,0.12);">'
            "</div>"
        )

    return (
        '<div style="text-align:center;font-size:3.5rem;margin:1rem 0;">'
        "🍫</div>"
    )


def _detect_products(text: str) -> list[dict]:
    """Detecta produtos citados no texto e retorna informações para exibição."""
    text_lower = text.lower()
    found = []
    seen_files = set()

    for keyword, product in _PRODUCT_MAP.items():
        if keyword in text_lower and product["file"] not in seen_files:
            image_path = _PRODUCTS_DIR / product["file"]
            if image_path.exists():
                found.append({**product, "path": str(image_path)})
                seen_files.add(product["file"])

    return found


def _show_product_images(products: list[dict]) -> None:
    """Exibe até quatro imagens de produtos detectados na resposta."""
    if not products:
        return

    columns = st.columns(min(len(products), 4))

    for column, product in zip(columns, products[:4]):
        with column:
            st.image(product["path"], use_container_width=True)
            st.caption(f"**{product['label']}**  \n{product['price']}")


def _init_state() -> None:
    """Inicializa os dados persistentes da sessão."""
    defaults = {
        "messages": [],
        "lead_name": "",
        "lead_phone": "",
        "lead_email": "",
        "chat_started": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _normalize_text(text: str) -> str:
    """Normaliza texto para comparações simples sem acentos."""
    replacements = str.maketrans(
        "áàãâäéèêëíìîïóòõôöúùûüç",
        "aaaaaeeeeiiiiooooouuuuc",
    )
    return text.lower().translate(replacements)


def _extract_name_from_message(text: str) -> str:
    """
    Captura nome em frases como 'me chamo Maria' ou em uma resposta isolada
    como 'Maria'. Não substitui um nome já coletado.
    """
    if st.session_state.lead_name:
        return st.session_state.lead_name

    clean = re.sub(r"[^A-Za-zÀ-ÿ' -]", "", text).strip()
    normalized = _normalize_text(clean)

    name_patterns = (
        r"(?:me chamo|meu nome e|sou o|sou a|pode me chamar de)\s+"
        r"([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ' -]{1,40})",
    )

    for pattern in name_patterns:
        match = re.search(pattern, clean, flags=re.IGNORECASE)
        if match:
            name = match.group(1).strip().split()[0].capitalize()
            st.session_state.lead_name = name
            return name

    ignored_messages = {
        "oi",
        "ola",
        "bom dia",
        "boa tarde",
        "boa noite",
        "tudo bem",
        "sim",
        "nao",
        "quero",
        "gostaria",
        "obrigado",
        "obrigada",
    }

    words = clean.split()

    if (
        1 <= len(words) <= 3
        and normalized not in ignored_messages
        and all(len(word) >= 2 for word in words)
    ):
        name = words[0].capitalize()
        st.session_state.lead_name = name
        return name

    return ""


def _extract_lead(text: str) -> None:
    """Captura nome, telefone e e-mail quando forem informados pelo cliente."""
    _extract_name_from_message(text)

    phone_digits = re.sub(r"\D", "", text)
    phones = re.findall(r"\d{10,11}", phone_digits)
    if phones and not st.session_state.lead_phone:
        st.session_state.lead_phone = phones[0]

    emails = re.findall(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
    if emails and not st.session_state.lead_email:
        st.session_state.lead_email = emails[0].lower()


def _name_prompt() -> str:
    """Resposta usada quando o lead ainda não informou um nome reconhecível."""
    return (
        "Que bom ter você por aqui na **Alma de Cacau**! 🍫\n\n"
        "Antes de te apresentar nossos bombons artesanais, como posso te chamar?"
    )


def _flavor_prompt(name: str) -> str:
    """Resposta obrigatória imediatamente após a identificação do nome."""
    return (
        f"Prazer, **{name}**! 🍫\n\n"
        "Você já tem algum sabor em mente ou prefere que eu apresente "
        "os sabores disponíveis?"
    )


def _call_groq() -> str:
    """Envia o histórico ao Groq após a etapa obrigatória de coleta do nome."""
    if not GROQ_API_KEY:
        return (
            "No momento não consigo acessar nossa assistente virtual. "
            "Por favor, tente novamente em instantes."
        )

    try:
        client = Groq(api_key=GROQ_API_KEY)

        context = (
            f"\n\nDADOS DA SESSÃO:\n"
            f"- Nome do cliente: {st.session_state.lead_name}\n"
            f"- O nome já foi obtido: sim\n"
            f"- Próximo foco comercial: sabores, quantidade e pedido.\n"
        )

        payload = [{"role": "system", "content": _SYSTEM_PROMPT + context}]
        payload.extend(
            {"role": message["role"], "content": message["content"]}
            for message in st.session_state.messages
        )

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=payload,
            temperature=0.3,
            max_tokens=500,
        )

        return response.choices[0].message.content.strip()

    except Exception:
        return (
            "Tive uma instabilidade no atendimento agora. "
            "Pode tentar enviar sua mensagem novamente, por favor?"
        )


def render() -> None:
    """Renderiza a página de atendimento da Cacau."""
    _init_state()

    st.markdown(_logo_html(), unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:#9a7050;font-style:italic;'
        'margin:-6px 0 1.5rem;font-size:0.9rem;">'
        "Atendimento personalizado &nbsp;·&nbsp; "
        "Trufas artesanais feitas à mão</p>",
        unsafe_allow_html=True,
    )

    if not st.session_state.chat_started:
        st.session_state.messages.append(
            {"role": "assistant", "content": _WELCOME}
        )
        st.session_state.chat_started = True

    for message in st.session_state.messages:
        avatar = (
            ":material/smart_toy:"
            if message["role"] == "assistant"
            else ":material/person:"
        )

        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                _show_product_images(_detect_products(message["content"]))

    if prompt := st.chat_input("Digite sua mensagem para a Cacau..."):
        had_name = bool(st.session_state.lead_name)

        _extract_lead(prompt)
        current_name = st.session_state.lead_name

        st.session_state.messages.append({"role": "user", "content": prompt})

        if not had_name and current_name:
            response = _flavor_prompt(current_name)
        elif not current_name:
            response = _name_prompt()
        else:
            with st.spinner("Cacau está preparando uma sugestão para você..."):
                response = _call_groq()

        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            st.markdown(response)
            _show_product_images(_detect_products(response))

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )
        st.rerun()

    st.divider()

    if st.button("🗑️ Limpar conversa", key="clr_chat"):
        for key in (
            "messages",
            "lead_name",
            "lead_phone",
            "lead_email",
            "chat_started",
        ):
            st.session_state.pop(key, None)

        st.rerun()