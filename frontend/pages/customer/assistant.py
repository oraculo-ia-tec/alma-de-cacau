"""
Assistente Cacau - Alma de Cacau
Chat guiado: nome -> sabor -> quantidade -> dados de entrega -> pagamento PIX (Asaas real)
Integracao direta com banco (SQLAlchemy) via services/ existentes do projeto.
"""

import base64
import json
import os
import re
import traceback
import uuid
from pathlib import Path

import streamlit as st
from groq import Groq

import config

_SYSTEM_PROMPT = """
Voce e a Cacau, assistente virtual da Alma de Cacau, marca premium de trufas e bombons artesanais feitos a mao.
Slogan da marca: "Pequenos pedacos de felicidade... transformando chocolate em lembranca."

CONTEXTO FIXO:
- Todo visitante que chega a este chat deseja comprar bombons artesanais.
- O nome do cliente ja foi coletado antes da sua resposta.
- A primeira pergunta apos saber o nome e sempre sobre preferencia de sabor.
- A marca trabalha com exatamente 7 sabores. Nunca cite sabores fora desta lista.

FLUXO OBRIGATORIO:
1. Se o cliente acabou de informar o nome, trate-o amigavelmente pelo nome uma unica vez e pergunte: "Voce ja tem algum sabor em mente ou prefere que eu apresente os sabores disponiveis?"
2. Nao pergunte sobre presente, evento, ocasiao ou data especial antes de o cliente mencionar esse assunto.
3. Se o cliente quiser conhecer os sabores, apresente as opcoes de modo breve, organizado e com os respectivos precos.
4. Depois de identificar os sabores, ajude com quantidade, caixa, embalagem e, quando apropriado, retirada ou entrega.
5. Pergunte sobre alergias somente quando houver recomendacao ou compra que envolva amendoim, castanha ou laticinios.
6. Nao peca o nome novamente e nao repita o nome em toda resposta.
7. Faca no maximo uma pergunta por resposta.
8. Nao invente produtos, precos, promocoes, estoque ou prazos.

CATALOGO OFICIAL - Trufas artesanais por unidade (os unicos 7 sabores existentes):
- Trufa de Pimenta - R$ 10,50 | equilibrio e intensidade.
- Trufa Doce de Leite com Amendoim - R$ 9,90 | pura nostalgia.
- Trufa de Castanha - R$ 9,50 | sofisticacao e crocancia.
- Trufa de Chocolate Branco - R$ 9,50 | delicadeza em cada mordida.
- Trufa de Pistache - R$ 10,50 | refinado e unico.
- Trufa de Amarula - R$ 9,90 | cremosidade e charme.
- Trufa de Cafe - R$ 8,90 | energia e sabor.

Caixas e embalagens:
- Caixa Degustacao, 9 unidades - R$ 69,90 | mix a escolha.
- Embalagem Standard - R$ 5,00.
- Embalagem Premium - R$ 12,00.
- Embalagem Luxury - R$ 25,00.

REGRAS:
- Use exatamente os nomes dos 7 produtos do catalogo ao recomenda-los, nunca crie sabores novos.
- Tom: acolhedor, elegante, breve, natural e voltado a venda.
- Ao mencionar um sabor, descreva a experiencia sensorial e, quando fizer sentido, a dica de degustacao.
"""

_INTENT_SYSTEM_PROMPT = """
Voce e um classificador de intencao de compra para um chat de vendas de bombons artesanais.
Analise a ULTIMA mensagem do cliente e responda APENAS com um JSON valido, sem texto extra, no formato:
{"intencao_compra": true|false, "sabor": "chave_do_sabor_ou_null", "quer_conhecer_sabores": true|false, "ja_conhece_marca": true|false}

Regras:
- "intencao_compra" e true somente se o cliente demonstrar decisao final de compra (ex: "quero esse", "vou levar", "pode fechar", "vou de pistache").
- "sabor" deve ser uma das chaves exatas: pimenta, "doce de leite", amendoim, castanha, "chocolate branco", pistache, amarula, cafe. Use null se nao houver sabor identificavel.
- "quer_conhecer_sabores" e true se o cliente pedir para ver as opcoes, sem ainda ter decidido.
- "ja_conhece_marca" e true se o cliente indicar que ja conhece a Alma de Cacau ou ja comprou antes.
- Nunca inclua explicacoes, apenas o JSON.
"""

from database.engine import get_db
from database.models import Product, PaymentMethod, DeliveryType
from services.customer_service import CustomerService
from services.order_service import OrderService
from services.payment_service import PaymentService
from services.notification_service import NotificationService
from schemas.customer import CreateCustomerInput, AddressInput
from schemas.order import CreateOrderInput, OrderItemInput
from schemas.payment import CreatePaymentInput
from adapters.asaas_adapter import create_customer as asaas_create_customer

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
_LOGO_PATH = Path(__file__).parents[3] / "logomarca.jpg"
_PRODUCTS_DIR = Path(__file__).parents[3] / "produtos"

_PRODUCT_MAP = {
    "pimenta": {"file": "pimenta.png", "label": "Trufa de Pimenta", "price": "R$ 10,50",
                "experiencia": "equilibrio e intensidade",
                "descricao": "O contraste perfeito entre o doce e o picante.",
                "degustacao": "Aprecie devagar, sentindo o calor suave."},
    "doce de leite": {"file": "doce-de-leite-com-amendoim.png", "label": "Trufa Doce de Leite com Amendoim",
                       "price": "R$ 9,90", "experiencia": "pura nostalgia",
                       "descricao": "Doce de leite cremoso com crocancia do amendoim.",
                       "degustacao": "Ideal com um cafe."},
    "amendoim": {"file": "doce-de-leite-com-amendoim.png", "label": "Trufa Doce de Leite com Amendoim",
                 "price": "R$ 9,90", "experiencia": "pura nostalgia",
                 "descricao": "Doce de leite cremoso com crocancia do amendoim.",
                 "degustacao": "Ideal com um cafe."},
    "castanha": {"file": "castanha.png", "label": "Trufa de Castanha", "price": "R$ 9,50",
                 "experiencia": "sofisticacao e crocancia",
                 "descricao": "Recheio cremoso com pedacos selecionados de castanha.",
                 "degustacao": "Harmoniza com um bom vinho."},
    "chocolate branco": {"file": "chocolate-branco.png", "label": "Trufa de Chocolate Branco", "price": "R$ 9,50",
                          "experiencia": "delicadeza em cada mordida",
                          "descricao": "Cremoso, suave e irresistivel.",
                          "degustacao": "Aprecie com calma."},
    "pistache": {"file": "pistache.png", "label": "Trufa de Pistache", "price": "R$ 10,50",
                 "experiencia": "refinado e unico",
                 "descricao": "Sabor nobre, cremoso e levemente amanteigado.",
                 "degustacao": "Deguste lentamente."},
    "amarula": {"file": "amarula.png", "label": "Trufa de Amarula", "price": "R$ 9,90",
                "experiencia": "cremosidade e charme",
                "descricao": "Toque suave e marcante do licor Amarula.",
                "degustacao": "Sirva geladinho."},
    "cafe": {"file": "cafe.png", "label": "Trufa de Cafe", "price": "R$ 8,90",
             "experiencia": "energia e sabor",
             "descricao": "Recheio intenso que desperta os sentidos.",
             "degustacao": "Companheiro ideal para o cafe da manha."},
}
_PRODUCT_MAP["café"] = _PRODUCT_MAP["cafe"]

_WELCOME = (
    "Ola! Seja muito bem-vindo(a) a **Alma de Cacau**! \U0001F36B\n\n"
    "Sou a **Cacau**, sua assistente de chocolates artesanais. "
    "Antes de te apresentar nossos bombons, como posso te chamar?"
)

_ASSISTANT_CSS = """
<style>
[data-testid="stSidebar"] { display: none !important; }
.cacau-hero { text-align: center; padding: 18px 0 8px 0; }
.cacau-logo-wrap { display: flex; justify-content: center; margin-bottom: 10px; }
.cacau-logo-wrap img {
    width: 96px; height: 96px; border-radius: 50%; object-fit: cover;
    border: 3px solid #F2A93B; animation: cacau-pulse 2.2s infinite;
}
@keyframes cacau-pulse {
    0%   { box-shadow: 0 0 0 0 rgba(232, 97, 60, 0.55); transform: scale(1); }
    70%  { box-shadow: 0 0 0 16px rgba(232, 97, 60, 0); transform: scale(1.03); }
    100% { box-shadow: 0 0 0 0 rgba(232, 97, 60, 0); transform: scale(1); }
}
.cacau-title {
    font-family: "Playfair Display", serif; font-size: 2rem; font-weight: 700;
    margin: 4px 0 0 0; background: linear-gradient(90deg, #E8613C, #F2A93B);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; animation: cacau-fadein 0.8s ease-out;
}
.cacau-subtitle { color: #6B7A3A; font-style: italic; font-size: 0.85rem; margin-top: 2px; }
@keyframes cacau-fadein {
    from { opacity: 0; transform: translateY(-6px); }
    to   { opacity: 1; transform: translateY(0); }
}
[data-testid="stChatMessage"] {
    background: #FFF3E4; border-radius: 14px; padding: 6px 10px;
    border: 1px solid rgba(232, 97, 60, 0.15);
}
</style>
"""


# ------------------------------------------------------------------
# Helpers de UI
# ------------------------------------------------------------------
def _logo_html() -> str:
    if _LOGO_PATH.exists():
        data = base64.b64encode(_LOGO_PATH.read_bytes()).decode()
        return f'<img src="data:image/jpeg;base64,{data}">'
    return "\U0001F36B"


def _hero_header_html() -> str:
    return f"""
    <div class="cacau-hero">
        <div class="cacau-logo-wrap">{_logo_html()}</div>
        <div class="cacau-title">Alma de Cacau</div>
        <div class="cacau-subtitle">Trufas artesanais feitas com alma</div>
    </div>
    """


def _detect_products(text: str):
    text_lower = text.lower()
    found = []
    for key, info in _PRODUCT_MAP.items():
        if key in text_lower and info not in found:
            found.append(info)
    return found


def _show_product_images(products: list):
    if not products:
        return
    cols = st.columns(len(products))
    for col, info in zip(cols, products):
        img_path = _PRODUCTS_DIR / info.get("file", "")
        with col:
            if info.get("file") and img_path.exists():
                caption = f"{info.get('label', '')} - {info.get('price', '')}"
                st.image(str(img_path), caption=caption, width="stretch")


def _extract_lead(prompt: str):
    if st.session_state.get("lead_name"):
        return
    match = re.search(r"(?:meu nome e|me chamo|sou o|sou a|eu sou)\s+([A-Za-z\u00c0-\u00fa]+)", prompt, re.IGNORECASE)
    if match:
        st.session_state.lead_name = match.group(1).strip().title()
    elif len(prompt.strip().split()) <= 3 and prompt.strip().isalpha():
        st.session_state.lead_name = prompt.strip().title()


def _name_prompt() -> str:
    return "Antes de continuarmos, como posso te chamar? \U0001F60A"


def _flavor_prompt(name: str) -> str:
    return (
        f"Prazer, {name}! \U0001F36B Voce ja tem algum sabor em mente ou prefere "
        "que eu apresente os sabores disponiveis?"
    )


# ------------------------------------------------------------------
# Groq
# ------------------------------------------------------------------
def _build_chat_history():
    history = [{"role": "system", "content": _SYSTEM_PROMPT}]
    for msg in st.session_state.messages:
        history.append({"role": msg["role"], "content": msg["content"]})
    return history


def _call_groq() -> str:
    client = Groq(api_key=GROQ_API_KEY)
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=_build_chat_history(),
        temperature=0.6,
        max_tokens=400,
    )
    return completion.choices[0].message.content.strip()


def _classify_intent(user_text: str) -> dict:
    default = {
        "intencao_compra": False, "sabor": None,
        "quer_conhecer_sabores": False, "ja_conhece_marca": False,
    }
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": _INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0, max_tokens=150,
        )
        raw = completion.choices[0].message.content.strip()
        raw = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
        default.update(json.loads(raw))
    except Exception:
        pass
    return default


# ------------------------------------------------------------------
# Integracao real: Customer / Address / Order / Payment / Asaas
# ------------------------------------------------------------------
def _get_or_create_customer(db) -> int:
    if st.session_state.get("customer_profile_id"):
        return st.session_state["customer_profile_id"]

    cs = CustomerService(db)
    email = st.session_state.get("lead_email") or f"lead_{uuid.uuid4().hex[:8]}@almadecacau.local"
    senha_temp = uuid.uuid4().hex[:12]

    profile, err = cs.register(CreateCustomerInput(
        email=email,
        password=senha_temp,
        full_name=st.session_state.get("lead_name", "Cliente"),
        phone=st.session_state.get("lead_whatsapp", ""),
        marketing_consent=False,
    ))
    if err:
        raise RuntimeError(err)

    db.flush()
    st.session_state["customer_profile_id"] = profile.id
    return profile.id


def _get_or_create_address(db, customer_id: int) -> int:
    cs = CustomerService(db)
    endereco_raw = st.session_state.get("lead_endereco") or ""
    partes = endereco_raw.split(",")
    street = partes[0].strip() if partes and partes[0].strip() else "Nao informado"
    number = partes[1].strip() if len(partes) > 1 and partes[1].strip() else "S/N"

    addr, err = cs.add_address(customer_id, AddressInput(
        label="Entrega",
        street=street,
        number=number,
        complement=None,
        neighborhood=st.session_state.get("lead_bairro") or "Nao informado",
        city=st.session_state.get("lead_cidade") or "Nao informado",
        state=(st.session_state.get("lead_uf") or "SP").upper()[:2],
        zip_code=st.session_state.get("lead_cep") or "00000000",
        is_default=True,
    ))
    if err:
        raise RuntimeError(err)
    db.flush()
    return addr.id


def _find_product_by_flavor_label(db, flavor_label: str):
    return db.query(Product).filter(
        Product.name.ilike(f"%{flavor_label}%"), Product.is_active == True
    ).first()


def _ensure_asaas_customer_id() -> str:
    if st.session_state.get("asaas_customer_id"):
        return st.session_state["asaas_customer_id"]

    cpf = (st.session_state.get("lead_cpf") or "").strip()
    if not cpf:
        raise RuntimeError("CPF e obrigatorio para gerar o pagamento PIX.")

    data, err = asaas_create_customer(
        name=st.session_state.get("lead_name", "Cliente"),
        cpf_cnpj=cpf,
        email=st.session_state.get("lead_email") or None,
        phone=st.session_state.get("lead_whatsapp") or None,
        external_reference=str(st.session_state.get("customer_profile_id", "")),
    )
    if err:
        raise RuntimeError(f"Erro ao criar cliente no Asaas: {err}")

    asaas_id = data.get("id")
    st.session_state["asaas_customer_id"] = asaas_id
    return asaas_id


def _register_order_and_payment() -> dict:
    order_info = st.session_state.get("order_confirmed") or {}
    flavor_label = order_info.get("flavor", "")
    quantity = int(order_info.get("quantity", 1))

    asaas_customer_id = _ensure_asaas_customer_id()

    with get_db() as db:
        customer_id = _get_or_create_customer(db)
        address_id = _get_or_create_address(db, customer_id)

        product = _find_product_by_flavor_label(db, flavor_label)
        if not product:
            raise RuntimeError(f"Produto '{flavor_label}' nao encontrado no catalogo.")

        order_service = OrderService(db)
        order, err = order_service.create_order(CreateOrderInput(
            customer_id=customer_id,
            delivery_type=DeliveryType.delivery,
            delivery_address_id=address_id,
            items=[OrderItemInput(product_id=product.id, quantity=quantity, item_notes=None)],
            coupon_code=None,
            customer_notes=st.session_state.get("lead_observacao", ""),
            desired_delivery_date=None,
        ))
        if err:
            raise RuntimeError(err)

        payment_service = PaymentService(db)
        payment, err = payment_service.create_payment(CreatePaymentInput(
            order_id=order.id,
            method=PaymentMethod.pix,
            asaas_customer_id=asaas_customer_id,
        ))
        if err:
            raise RuntimeError(err)

        pix_data, err = payment_service.get_pix_qr_code(payment.id)

        notif = NotificationService(db)
        notif.notify_order_confirmation(
            order_number=order.order_number,
            customer_name=st.session_state.get("lead_name", "Cliente"),
            total=f"{order.total:.2f}",
            customer_id=customer_id,
        )

        return {
            "order_number": order.order_number,
            "payment_id": payment.id,
            "total": float(order.total),
            "pix": pix_data or {},
        }


def _render_payment_block():
    st.chat_message("assistant", avatar=":material/smart_toy:").markdown(
        "Perfeito! Para gerar o pagamento PIX, preciso confirmar seus dados de entrega \U0001F4E6"
    )
    with st.container(border=True):
        st.session_state["lead_name"] = st.text_input("Nome completo", value=st.session_state.get("lead_name", ""))
        st.session_state["lead_whatsapp"] = st.text_input("WhatsApp", value=st.session_state.get("lead_whatsapp", ""))
        st.session_state["lead_endereco"] = st.text_input("Rua e numero (ex: Rua das Flores, 123)", value=st.session_state.get("lead_endereco", ""))
        col_a, col_b = st.columns(2)
        with col_a:
            st.session_state["lead_bairro"] = st.text_input("Bairro", value=st.session_state.get("lead_bairro", ""))
            st.session_state["lead_cidade"] = st.text_input("Cidade", value=st.session_state.get("lead_cidade", ""))
        with col_b:
            st.session_state["lead_uf"] = st.text_input("UF", value=st.session_state.get("lead_uf", ""), max_chars=2)
            st.session_state["lead_cep"] = st.text_input("CEP", value=st.session_state.get("lead_cep", ""))
        st.session_state["lead_email"] = st.text_input("E-mail", value=st.session_state.get("lead_email", ""))
        st.session_state["lead_cpf"] = st.text_input("CPF", value=st.session_state.get("lead_cpf", ""))

        missing = []
        if not st.session_state.get("lead_name"):
            missing.append("nome")
        if not st.session_state.get("lead_endereco"):
            missing.append("endereco")
        if not st.session_state.get("lead_whatsapp"):
            missing.append("whatsapp")
        if not st.session_state.get("lead_cpf"):
            missing.append("cpf")

        ready = len(missing) == 0
        if not ready:
            st.info("Faltam: " + ", ".join(missing))
        else:
            st.success("Pedido pronto para gerar o pagamento.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("\U0001F4B3 Gerar PIX", key="gerar_pix_db", width="stretch", disabled=not ready):
                try:
                    result = _register_order_and_payment()
                    st.session_state["db_payment_result"] = result
                    st.session_state["db_payment_error"] = ""
                except Exception as exc:
                    st.session_state["db_payment_result"] = None
                    st.session_state["db_payment_error"] = str(exc)
        with col2:
            if st.button("\u21A9\uFE0F Voltar para o chat", key="voltar_pagamento_db", width="stretch"):
                st.session_state.awaiting_payment = False
                st.rerun()

        if st.session_state.get("db_payment_error"):
            st.error(st.session_state["db_payment_error"])

        result = st.session_state.get("db_payment_result")
        if result:
            st.markdown(f"### Pedido {result['order_number']} criado!")
            st.caption(f"Total: R$ {result['total']:.2f}".replace(".", ","))
            pix = result.get("pix") or {}
            if pix.get("payload"):
                st.code(pix["payload"], language="text")
            if pix.get("encodedImage"):
                st.image(f"data:image/png;base64,{pix['encodedImage']}")
    st.stop()


# ------------------------------------------------------------------
# Fluxo de compra estruturado (sabor -> quantidade)
# ------------------------------------------------------------------
def _render_quantity_selector(flavor_key: str, flavor_info: dict):
    with st.container(border=True):
        img_path = _PRODUCTS_DIR / flavor_info.get("file", "")
        if flavor_info.get("file") and img_path.exists():
            st.image(str(img_path), caption=flavor_info.get("label", ""), width="stretch")

        st.markdown(f"**{flavor_info.get('label', '')}** - {flavor_info.get('price', '')}")
        st.caption(f"\u2728 {flavor_info.get('experiencia', '').capitalize()}")
        st.write(flavor_info.get("descricao", ""))
        st.info(f"\U0001F36B **Como degustar:** {flavor_info.get('degustacao', '')}")

        qty_state_key = f"qty_{flavor_key}"
        if qty_state_key not in st.session_state:
            st.session_state[qty_state_key] = 1

        st.session_state[qty_state_key] = st.number_input(
            "Quantidade desejada",
            min_value=1,
            max_value=50,
            step=1,
            value=int(st.session_state[qty_state_key]),
            format="%d",
        )
        number = st.session_state[qty_state_key]
        st.write("Quantidade atual:", number)

        try:
            price_value = float(flavor_info.get("price", "0").replace("R$", "").replace(",", ".").strip())
            subtotal = number * price_value
            st.caption(f"Subtotal: R$ {subtotal:.2f}".replace(".", ","))
        except (ValueError, AttributeError):
            pass

        col_confirm, col_back = st.columns(2)
        with col_confirm:
            if st.button("\u2705 Confirmar pedido", key=f"confirm_{flavor_key}", width="stretch"):
                st.session_state.order_confirmed = {
                    "flavor": flavor_info.get("label", ""),
                    "quantity": number,
                    "unit_price": flavor_info.get("price", ""),
                }
                st.session_state.awaiting_quantity = False
                st.session_state.awaiting_payment = True
                st.rerun()
        with col_back:
            if st.button("\u21A9\uFE0F Voltar para o chat", key=f"back_{flavor_key}", width="stretch"):
                st.session_state.awaiting_quantity = False
                st.rerun()


def _maybe_stop_for_purchase(prompt: str):
    intent = _classify_intent(prompt)
    st.session_state.last_intent = intent
    if intent.get("intencao_compra") and intent.get("sabor"):
        flavor_key = str(intent["sabor"]).lower().strip()
        flavor_info = _PRODUCT_MAP.get(flavor_key)
        if flavor_info:
            st.session_state.pending_flavor = flavor_key
            st.session_state.pending_flavor_info = flavor_info
            st.session_state.awaiting_quantity = True


def _render_pending_quantity_block():
    if not st.session_state.get("awaiting_quantity"):
        return
    flavor_key = st.session_state.get("pending_flavor")
    flavor_info = st.session_state.get("pending_flavor_info")
    if not flavor_key or not flavor_info:
        st.session_state.awaiting_quantity = False
        return
    st.chat_message("assistant", avatar=":material/smart_toy:").markdown(
        f"Otima escolha! Vamos definir a quantidade da sua **{flavor_info.get('label', '')}** \U0001F447"
    )
    _render_quantity_selector(flavor_key, flavor_info)
    st.stop()


# ------------------------------------------------------------------
# Inicializacao de estado
# ------------------------------------------------------------------
def _init_session_state():
    defaults = {
        "messages": [], "lead_name": None, "lead_phone": None, "lead_email": None,
        "lead_endereco": None, "lead_whatsapp": None, "lead_cpf": None,
        "lead_bairro": None, "lead_cidade": None, "lead_uf": None, "lead_cep": None,
        "chat_started": False, "awaiting_quantity": False, "awaiting_payment": False,
        "pending_flavor": None, "pending_flavor_info": None,
        "order_confirmed": None, "last_intent": None,
        "customer_profile_id": None, "asaas_customer_id": None,
        "db_payment_result": None, "db_payment_error": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ------------------------------------------------------------------
# Pagina principal
# ------------------------------------------------------------------
def render():
    try:
        _render_body()
    except Exception as e:
        st.error(f"\u26A0\uFE0F Erro na renderizacao do assistente: {e}")
        st.code(traceback.format_exc())


def _render_body():
    _init_session_state()
    st.markdown(_ASSISTANT_CSS, unsafe_allow_html=True)
    st.markdown(_hero_header_html(), unsafe_allow_html=True)

    if not st.session_state.chat_started:
        st.session_state.messages.append({"role": "assistant", "content": _WELCOME})
        st.session_state.chat_started = True

    for message in st.session_state.messages:
        avatar = ":material/smart_toy:" if message["role"] == "assistant" else ":material/person:"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
        if message["role"] == "assistant" and not st.session_state.get("awaiting_quantity"):
            _show_product_images(_detect_products(message["content"]))

    _render_pending_quantity_block()

    if st.session_state.get("awaiting_payment"):
        _render_payment_block()

    if prompt := st.chat_input("Digite sua mensagem para a Cacau...", key="cacau_chat_input"):
        had_name = bool(st.session_state.lead_name)
        _extract_lead(prompt)
        current_name = st.session_state.lead_name

        st.session_state.messages.append({"role": "user", "content": prompt})

        if had_name and current_name:
            _maybe_stop_for_purchase(prompt)

        if not had_name and current_name:
            response = _flavor_prompt(current_name)
        elif not current_name:
            response = _name_prompt()
        elif st.session_state.get("awaiting_quantity"):
            label = st.session_state.pending_flavor_info.get("label", "")
            response = f"Perfeito! So falta voce confirmar a quantidade da {label} aqui abaixo \U0001F447"
        else:
            with st.spinner("Cacau esta preparando uma sugestao para voce..."):
                response = _call_groq()

        with st.chat_message("assistant", avatar=":material/smart_toy:"):
            st.markdown(response)
        if not st.session_state.get("awaiting_quantity"):
            _show_product_images(_detect_products(response))

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    st.divider()
    if st.button("Limpar conversa", key="clr_chat"):
        for key in [
            "messages", "lead_name", "lead_phone", "lead_email", "lead_endereco",
            "lead_whatsapp", "lead_cpf", "lead_bairro", "lead_cidade", "lead_uf", "lead_cep",
            "chat_started", "awaiting_quantity", "awaiting_payment",
            "pending_flavor", "pending_flavor_info", "order_confirmed", "last_intent",
            "customer_profile_id", "asaas_customer_id", "db_payment_result", "db_payment_error",
        ]:
            st.session_state.pop(key, None)
        st.rerun()


if __name__ == "__main__":
    render()
