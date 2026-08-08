"""
Assistente Cacau — Alma de Cacau
Fluxo conversacional com máquina de estados guiada.
Fluxo completo: saudação → sabor → quantidade → adicional →
confirmação → LGPD → nome → endereço → CPF → PIX → polling → entrega.

Baseado em FLUXO_CONVERSACIONAL.md (adaptado para chocolates artesanais Alma de Cacau).
"""
from __future__ import annotations

import base64
import json
import re
import traceback
import uuid
from pathlib import Path
from typing import Optional

import streamlit as st
from groq import Groq

import config
from services.flow_manager import CacauFlowManager, PRODUCT_MAP

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTES DE CAMINHOS
# ──────────────────────────────────────────────────────────────────────────────

_ROOT         = Path(__file__).resolve().parents[3]
_LOGO_PATH    = _ROOT / "cacau" / "img" / "cacau-image.png"
_PRODUCTS_DIR = _ROOT / "produtos"
_VIDEOS_DIR   = _ROOT / "cacau" / "videos"

# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPTS
# ──────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """
Você é a Cacau, assistente virtual da Alma de Cacau, marca premium de trufas e bombons artesanais feitos à mão.
Slogan da marca: "Pequenos pedaços de felicidade... transformando chocolate em lembrança."

CONTEXTO:
- Todo visitante neste chat deseja comprar bombons artesanais.
- O nome do cliente já foi coletado antes da sua resposta.
- Após saber o nome, pergunte sobre preferência de sabor.
- A marca trabalha com exatamente 7 sabores. Nunca cite sabores fora desta lista.

FLUXO OBRIGATÓRIO:
1. Se o cliente acabou de informar o nome, trate-o amigavelmente pelo nome UMA ÚNICA VEZ e pergunte:
   "Você já tem algum sabor em mente ou prefere que eu apresente os sabores disponíveis?"
2. Não pergunte sobre presente ou ocasião antes de o cliente mencionar esse assunto.
3. Se o cliente quiser conhecer os sabores, apresente as opções com preços de forma breve e organizada.
4. Depois de identificar o sabor, ajude com quantidade e embalagem.
5. Pergunte sobre alergias somente quando a escolha envolver amendoim, castanha ou laticínios.
6. Não peça o nome novamente. Não repita o nome em toda resposta.
7. Faça NO MÁXIMO uma pergunta por resposta.
8. Não invente produtos, preços, promoções, estoque ou prazos.

CATÁLOGO OFICIAL (os únicos 7 sabores existentes):
- Trufa de Pimenta — R$ 10,50 | equilíbrio e intensidade
- Trufa Doce de Leite com Amendoim — R$ 9,90 | pura nostalgia
- Trufa de Castanha — R$ 9,50 | sofisticação e crocância
- Trufa de Chocolate Branco — R$ 9,50 | delicadeza em cada mordida
- Trufa de Pistache — R$ 10,50 | refinado e único
- Trufa de Amarula — R$ 9,90 | cremosidade e charme
- Trufa de Cafe — R$ 8,90 | energia e sabor

Caixas e embalagens:
- Caixa Degustação (9 unidades) — R$ 69,90 | mix à escolha
- Embalagem Standard — R$ 5,00
- Embalagem Premium — R$ 12,00
- Embalagem Luxury — R$ 25,00

REGRAS:
- Use exatamente os nomes dos 7 produtos ao recomendá-los.
- Tom: acolhedor, elegante, breve, natural e voltado à venda.
- Ao mencionar um sabor, descreva a experiência sensorial.
"""

_INTENT_PROMPT = """
Você é um classificador de intenção para um chat de vendas de bombons artesanais.
Analise a ÚLTIMA mensagem do cliente e responda APENAS com JSON válido, sem texto extra:
{"intencao_compra": true|false, "sabor": "chave_ou_null", "quer_conhecer_sabores": true|false}

Chaves de sabor válidas: "pimenta", "doce de leite", "castanha", "chocolate branco",
                         "pistache", "amarula", "cafe"
- "intencao_compra": true se cliente demonstrar decisão de compra ("vou de pistache", "quero esse").
- "sabor": chave exata detectada, ou null se nenhum.
- "quer_conhecer_sabores": true se pedir para ver opções sem ter decidido.
Nunca inclua explicações. Apenas o JSON.
"""

# ──────────────────────────────────────────────────────────────────────────────
# CSS DO ASSISTENTE
# ──────────────────────────────────────────────────────────────────────────────

_ASSISTANT_CSS = """
<style>
[data-testid="stSidebar"] { display: none !important; }
.cacau-hero { text-align: center; padding: 18px 0 8px 0; }
.cacau-logo-wrap { display: flex; justify-content: center; margin-bottom: 10px; }
.cacau-logo-wrap img {
    width: 200px; height: 200px; border-radius: 50%; object-fit: cover;
    border: 4px solid #F2A93B; animation: cacauPulse 2.2s infinite;
}
@keyframes cacauPulse {
    0%   { box-shadow: 0 0 0 0 rgba(232,97,60,0.55); transform: scale(1); }
    70%  { box-shadow: 0 0 0 16px rgba(232,97,60,0); transform: scale(1.03); }
    100% { box-shadow: 0 0 0 0 rgba(232,97,60,0); transform: scale(1); }
}
.cacau-title {
    font-family: "Playfair Display", serif; font-size: 2rem; font-weight: 700;
    margin: 4px 0 0 0;
    background: linear-gradient(90deg, #E8613C, #F2A93B);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.cacau-subtitle { color: #6B7A3A; font-style: italic; font-size: 0.85rem; margin-top: 2px; }
[data-testid="stChatMessage"] {
    background: #FFF3E4; border-radius: 14px; padding: 6px 10px;
    border: 1px solid rgba(232,97,60,0.15);
}
section[data-testid="stBottom"] > div {
    background: linear-gradient(180deg, transparent, #FFF3E4 70%); padding-top: 8px;
}
[data-testid="stChatInput"] {
    border: 2px solid #F2A93B !important; border-radius: 24px !important;
    background: #FFFAF4 !important; box-shadow: 0 4px 18px rgba(232,97,60,0.13) !important;
}
[data-testid="stChatInput"] textarea { font-size: 0.96rem !important; color: #3D2210 !important; }
[data-testid="stChatInput"] textarea::placeholder { color: #C49A6C !important; font-style: italic; }
[data-testid="stChatInput"] button svg { fill: #E8613C !important; }
</style>
"""

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS DE UI
# ──────────────────────────────────────────────────────────────────────────────

def _logo_html() -> str:
    if _LOGO_PATH.exists():
        data = base64.b64encode(_LOGO_PATH.read_bytes()).decode()
        return f'<img src="data:image/png;base64,{data}">'
    return "🍫"


@st.cache_resource(show_spinner=False)
def _cacau_avatar():
    """Retorna imagem PIL ou emoji da Cacau para avatar no chat."""
    try:
        from PIL import Image as _PIL
        if _LOGO_PATH.exists():
            img = _PIL.open(str(_LOGO_PATH))
            img.load()
            return img
    except Exception:
        pass
    return "🍫"


def _hero_html() -> str:
    return (
        '<div class="cacau-hero">'
        f'<div class="cacau-logo-wrap">{_logo_html()}</div>'
        '<div class="cacau-title">Alma de Cacau</div>'
        '<div class="cacau-subtitle">Trufas artesanais feitas com alma</div>'
        "</div>"
    )


def _detect_products_in_text(text: str) -> list[dict]:
    """Detecta produtos mencionados em texto e retorna lista de infos únicas."""
    lower = text.lower()
    found: list[dict] = []
    seen: set[str] = set()
    for info in PRODUCT_MAP.values():
        if info["label"] not in seen and info["label"].lower() in lower:
            found.append(info)
            seen.add(info["label"])
    return found


def _show_product_images(products: list[dict]) -> None:
    if not products:
        return
    cols = st.columns(len(products))
    for col, info in zip(cols, products):
        img_path = _PRODUCTS_DIR / info.get("file", "")
        with col:
            if img_path.exists():
                st.image(
                    str(img_path),
                    caption=f"{info['label']} — {info['price_str']}",
                    use_container_width=True,
                )


# ──────────────────────────────────────────────────────────────────────────────
# GROQ — LLM
# ──────────────────────────────────────────────────────────────────────────────

def _call_groq() -> str:
    """Resposta da Cacau via Groq/Llama usando fm_messages como histórico."""
    history = [{"role": "system", "content": _SYSTEM_PROMPT}]
    for msg in st.session_state.fm_messages:
        history.append({"role": msg["role"], "content": msg["content"]})
    try:
        client = Groq(api_key=config.GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=history,
            temperature=0.6,
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Desculpe, tive um problema momentâneo. Pode repetir? 😊 (Erro: {e})"


def _classify_intent(user_text: str) -> dict:
    """Classifica intenção de compra via LLM (fallback de detecção)."""
    default: dict = {"intencao_compra": False, "sabor": None, "quer_conhecer_sabores": False}
    try:
        client = Groq(api_key=config.GROQ_API_KEY)
        resp = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": _INTENT_PROMPT},
                {"role": "user",   "content": user_text},
            ],
            temperature=0,
            max_tokens=100,
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
        default.update(json.loads(raw))
    except Exception:
        pass
    return default


# ──────────────────────────────────────────────────────────────────────────────
# FLOW MANAGER — instância cacheada
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_resource(show_spinner=False)
def _get_flow_manager() -> CacauFlowManager:
    return CacauFlowManager()


# ──────────────────────────────────────────────────────────────────────────────
# INICIALIZAÇÃO DE ESTADO
# ──────────────────────────────────────────────────────────────────────────────

def _init_state() -> None:
    _get_flow_manager().init_state()

    extras = {
        "fm_lead_name":        None,
        "fm_asaas_cid":        None,
        "fm_pix_error":        "",
        "fm_video_seen":       False,
        "_had_name_before":    False,
    }
    for k, v in extras.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if not st.session_state.fm_chat_started:
        st.session_state.fm_messages.append({
            "role":    "assistant",
            "content": (
                "Olá! Seja muito bem-vindo(a) à **Alma de Cacau**! 🍫\n\n"
                "Sou a **Cacau**, sua assistente de chocolates artesanais. "
                "Antes de te apresentar nossos bombons, como posso te chamar?"
            ),
        })
        st.session_state.fm_chat_started = True


# ──────────────────────────────────────────────────────────────────────────────
# WIDGETS DE ESTADO
# ──────────────────────────────────────────────────────────────────────────────

def _render_quantity_widget() -> None:
    """Seletor numérico de quantidade — flow_state: aguardando_quantidade."""
    flavor_key  = st.session_state.get("fm_flavor_key")
    flavor_info = st.session_state.get("fm_flavor_info")
    if not flavor_key or not flavor_info:
        st.session_state.flow_state = "aguardando_intencao"
        st.rerun()
        return

    fm = _get_flow_manager()
    with st.container(border=True):
        col_produto, col_widget = st.columns([1, 1], gap="large")

        # ── Coluna esquerda: informações do produto ──
        with col_produto:
            img_path = _PRODUCTS_DIR / flavor_info.get("file", "")
            if img_path.exists():
                st.image(str(img_path), caption=flavor_info["label"], use_container_width=True)

            st.markdown(f"**{flavor_info['label']}** — {flavor_info['price_str']}")
            st.caption(f"✨ {flavor_info['experiencia']}")
            st.write(flavor_info["descricao"])
            st.info(f"🍫 **Como degustar:** {flavor_info['degustacao']}")

        # ── Coluna direita: seleção de quantidade ──
        with col_widget:
            st.markdown("#### Quantidade")

            # Usa a key do widget diretamente no session_state (evita conflito value/key)
            qty_key = f"qty_{flavor_key}"
            if qty_key not in st.session_state:
                st.session_state[qty_key] = 1

            qty = st.number_input(
                "Quantidade",
                min_value=1,
                max_value=50,
                step=1,
                key=qty_key,
                label_visibility="collapsed",
            )

            subtotal = round(flavor_info["price"] * qty, 2)
            st.markdown(f"**Subtotal:** R$ {subtotal:.2f}".replace(".", ","))

            st.divider()

            if st.button("✅ Adicionar ao pedido", key=f"add_{flavor_key}", use_container_width=True):
                fm.add_to_cart(flavor_key, flavor_info, qty)
                # Limpa estado do widget para próxima seleção
                if qty_key in st.session_state:
                    del st.session_state[qty_key]
                st.session_state.fm_flavor_key  = None
                st.session_state.fm_flavor_info = None
                st.session_state.flow_state = "aguardando_adicional"
                st.session_state.fm_messages.append({
                    "role":    "assistant",
                    "content": (
                        f"Adicionei **{qty}× {flavor_info['label']}** ao pedido! 🎉\n\n"
                        f"Subtotal: R$ {subtotal:.2f}\n\n"
                        "Deseja adicionar mais algum item ou finalizar o pedido?"
                    ).replace(".", ",", 1),
                })
                st.rerun()

            if st.button("↩️ Voltar ao chat", key=f"back_{flavor_key}", use_container_width=True):
                # Limpa estado do widget
                if qty_key in st.session_state:
                    del st.session_state[qty_key]
                st.session_state.fm_flavor_key  = None
                st.session_state.fm_flavor_info = None
                st.session_state.flow_state = "aguardando_sabor"
                st.rerun()


def _render_order_summary() -> None:
    """Resumo do carrinho com confirmação — flow_state: aguardando_confirmacao_total."""
    fm    = _get_flow_manager()
    cart  = st.session_state.fm_cart
    total = fm.cart_total()

    if not cart:
        st.session_state.flow_state = "aguardando_intencao"
        st.rerun()
        return

    with st.container(border=True):
        st.markdown("### 🧾 Resumo do Pedido")
        for item in cart:
            st.markdown(
                f"• **{item['label']}** × {item['quantity']} unid. "
                f"→ R$ {item['subtotal']:.2f}".replace(".", ",")
            )
        st.markdown("---")
        st.markdown(
            f"### TOTAL: R$ {total:.2f}".replace(".", ",")
        )

        col_add, col_confirm = st.columns(2)
        with col_add:
            if st.button("➕ Adicionar mais", key="resumo_add", use_container_width=True):
                st.session_state.flow_state = "aguardando_adicional"
                st.session_state.fm_messages.append({
                    "role": "assistant", "content": "Claro! Qual sabor você gostaria de adicionar?",
                })
                st.rerun()
        with col_confirm:
            if st.button("✅ Confirmar pedido", key="resumo_confirm", use_container_width=True, type="primary"):
                st.session_state.flow_state = "aguardando_autorizacao_dados"
                st.session_state.fm_messages.append({
                    "role":    "assistant",
                    "content": "Ótimo! Para processar o pedido, precisarei de algumas informações. Confira a tela abaixo 🔐",
                })
                st.rerun()


def _render_lgpd_screen() -> None:
    """Consentimento LGPD — flow_state: aguardando_autorizacao_dados."""
    fm    = _get_flow_manager()
    total = fm.cart_total()

    with st.container(border=True):
        st.markdown("### 🔐 Autorização de Dados")
        st.markdown(
            f"Para concluir seu pedido de **R$ {total:.2f}**, precisaremos coletar:".replace(".", ",")
        )
        st.info(
            "📝 **Nome** para a entrega\n\n"
            "📍 **Endereço** completo de entrega\n\n"
            "🔒 **CPF** para geração do PIX (processado com segurança pelo Asaas)"
        )
        st.caption("Dados usados exclusivamente para esta transação. LGPD 13.709/2018.")

        col_ok, col_cancel = st.columns(2)
        with col_ok:
            if st.button("✅ EU CONFIRMO", key="lgpd_ok", use_container_width=True, type="primary"):
                st.session_state.flow_state = "coletando_nome_entrega"
                st.session_state.fm_messages.append({
                    "role": "assistant", "content": "Perfeito! 😊 Qual o **nome** de quem vai receber o pedido?",
                })
                st.rerun()
        with col_cancel:
            if st.button("❌ Cancelar", key="lgpd_cancel", use_container_width=True):
                st.session_state.flow_state = "aguardando_confirmacao_total"
                st.session_state.fm_messages.append({
                    "role": "assistant", "content": "Entendido. Seu pedido continua reservado. Deseja revisá-lo?",
                })
                st.rerun()


def _render_gerando_pix() -> None:
    """Gera cliente no Asaas, cria pedido e cobrança PIX — flow_state: gerando_pix."""
    if st.session_state.get("fm_pix_result"):
        st.session_state.flow_state = "aguardando_pagamento_pix"
        st.rerun()
        return

    with st.spinner("Preparando seu PIX com segurança... 🔐"):
        try:
            result = _build_pix_payment()
            st.session_state.fm_pix_result   = result.get("pix") or {}
            st.session_state.fm_payment_id   = result.get("payment_id")
            st.session_state.fm_order_number = result.get("order_number")
            st.session_state.fm_pix_error    = result.get("pix_error", "")
            st.session_state.fm_asaas_cid    = result.get("asaas_customer_id")
            st.session_state.flow_state = "aguardando_pagamento_pix"
            st.session_state.fm_messages.append({
                "role":    "assistant",
                "content": (
                    f"✅ Pedido **{result['order_number']}** criado!\n\n"
                    "Escaneie o QR Code PIX abaixo ou use o código Copia e Cola. "
                    "Confirmarei automaticamente quando o pagamento chegar. 🍫"
                ),
            })
        except Exception as exc:
            st.session_state.fm_pix_error = str(exc)
            st.session_state.fm_pix_result = None
            st.session_state.flow_state = "coletando_cpf"
            st.session_state.fm_messages.append({
                "role":    "assistant",
                "content": f"Tive um problema ao gerar o PIX: {exc}\n\nPode tentar novamente? Digite seu CPF:",
            })
    st.rerun()


def _build_pix_payment() -> dict:
    """Cria cliente Asaas, pedido no banco e cobrança PIX. Retorna info do resultado."""
    from database.engine import get_db
    from database.models import Product, PaymentMethod, DeliveryType
    from services.customer_service import CustomerService
    from services.order_service import OrderService
    from services.payment_service import PaymentService
    from schemas.customer import CreateCustomerInput, AddressInput
    from schemas.order import CreateOrderInput, OrderItemInput
    from schemas.payment import CreatePaymentInput
    from adapters.asaas_adapter import create_customer as asaas_create_customer

    fm      = _get_flow_manager()
    cart    = st.session_state.fm_cart
    cpf     = st.session_state.fm_cpf or ""
    name    = st.session_state.fm_nome_entrega or st.session_state.get("fm_lead_name") or "Cliente"
    address = st.session_state.fm_endereco_entrega or "Não informado"

    # Criar/buscar cliente no Asaas
    asaas_cid = st.session_state.get("fm_asaas_cid") or st.session_state.get("asaas_customer_id")
    if not asaas_cid:
        cust_email = (
            st.session_state.get("customer_email")
            or f"lead_{uuid.uuid4().hex[:8]}@almadecacau.local"
        )
        cdata, cerr = asaas_create_customer(
            name=name,
            cpf_cnpj=cpf,
            email=cust_email,
            external_reference=str(st.session_state.get("customer_id") or ""),
        )
        if cerr:
            raise RuntimeError(f"Erro ao criar cliente no Asaas: {cerr}")
        asaas_cid = cdata["id"]
        st.session_state.fm_asaas_cid = asaas_cid

    with get_db() as db:
        # Garantir CustomerProfile no banco
        customer_id = (
            st.session_state.get("customer_id")
            or st.session_state.get("fm_customer_profile_id")
        )
        if not customer_id:
            cs = CustomerService(db)
            email = (
                st.session_state.get("customer_email")
                or f"lead_{uuid.uuid4().hex[:8]}@almadecacau.local"
            )
            profile, perr = cs.register(CreateCustomerInput(
                email=email,
                password=uuid.uuid4().hex[:12],
                full_name=name,
                phone="",
                marketing_consent=False,
            ))
            if perr:
                raise RuntimeError(perr)
            db.flush()
            customer_id = profile.id
            st.session_state.fm_customer_profile_id = customer_id

        # Endereço de entrega
        cs2 = CustomerService(db)
        partes = address.split(",")
        raw_street = partes[0].strip() if partes else ""
        # Garante min_length=3 exigido pela AddressInput
        street = raw_street if len(raw_street) >= 3 else (f"Rua {raw_street}" if raw_street else "Endereco nao informado")
        number = partes[1].strip() if len(partes) > 1 else "S/N"
        addr, aerr = cs2.add_address(customer_id, AddressInput(
            label="Entrega",
            street=street,
            number=number,
            complement=None,
            neighborhood="Não informado",
            city="Não informado",
            state="SP",
            zip_code="00000000",
            is_default=True,
        ))
        if aerr:
            raise RuntimeError(aerr)
        db.flush()

        # Mapeia itens do carrinho para produtos do banco
        order_items: list[OrderItemInput] = []
        for cart_item in cart:
            # Busca por SKU (preferencial) ou por nome — evita problemas de acento
            sku = cart_item.get("sku", "")
            if sku:
                product = db.query(Product).filter_by(sku=sku, is_active=True).first()
            else:
                product = (
                    db.query(Product)
                    .filter(
                        Product.name.ilike(f"%{cart_item['label']}%"),
                        Product.is_active == True,
                    )
                    .first()
                )
            if not product:
                raise RuntimeError(
                    f"Produto '{cart_item['label']}' (SKU: {sku}) não encontrado no catálogo. "
                    "Execute o seed para popular o catálogo."
                )
            order_items.append(OrderItemInput(
                product_id=product.id,
                quantity=cart_item["quantity"],
                item_notes=None,
            ))

        # Criação do pedido
        order_svc = OrderService(db)
        order, oerr = order_svc.create_order(CreateOrderInput(
            customer_id=customer_id,
            delivery_type=DeliveryType.delivery,
            delivery_address_id=addr.id,
            items=order_items,
            coupon_code=None,
            customer_notes="",
            desired_delivery_date=None,
        ))
        if oerr:
            raise RuntimeError(oerr)

        # Criação do pagamento PIX
        pay_svc = PaymentService(db)
        payment, pay_err = pay_svc.create_payment(CreatePaymentInput(
            order_id=order.id,
            method=PaymentMethod.pix,
            asaas_customer_id=asaas_cid,
        ))
        if pay_err:
            raise RuntimeError(pay_err)

        pix_data, pix_err = pay_svc.get_pix_qr_code(payment.id)

        # Lê atributos DENTRO do bloco with — evita DetachedInstanceError após db.close()
        _result = {
            "order_number":      order.order_number,
            "payment_id":        payment.id,
            "asaas_customer_id": asaas_cid,
            "total":             float(order.total),
            "pix":               pix_data or {},
            "pix_error":         pix_err or "",
        }

    return _result


def _render_pix_panel() -> None:
    """Exibe QR Code PIX e ativa polling — flow_state: aguardando_pagamento_pix."""
    pix   = st.session_state.get("fm_pix_result") or {}
    err   = st.session_state.get("fm_pix_error", "")
    total = _get_flow_manager().cart_total()

    with st.container(border=True):
        st.markdown("### 💸 Pagamento via PIX")
        st.caption(f"Total: **R$ {total:.2f}**".replace(".", ","))

        encoded = pix.get("encodedImage") or pix.get("EncodedImage") or ""
        payload = pix.get("payload") or pix.get("Payload") or ""

        if encoded or payload:
            col_qr, col_code = st.columns(2)
            with col_qr:
                if encoded:
                    st.image(
                        f"data:image/png;base64,{encoded}",
                        caption="Aponte a câmera do seu banco",
                        use_container_width=True,
                    )
                else:
                    st.info("QR Code não disponível")
            with col_code:
                st.markdown("**📋 Copia e Cola:**")
                if payload:
                    st.code(payload, language="text")
                    st.caption("Cole este código no app do seu banco.")
                else:
                    st.warning("Código PIX não retornado pela API.")
        elif err:
            st.error(f"Erro ao gerar QR Code: {err}")
            if st.button("🔄 Tentar novamente com novo CPF", key="pix_retry"):
                st.session_state.fm_pix_result  = None
                st.session_state.fm_pix_error   = ""
                st.session_state.fm_cpf         = None
                st.session_state.flow_state = "coletando_cpf"
                st.session_state.fm_messages.append({
                    "role": "assistant",
                    "content": "Por favor, informe seu CPF novamente (somente números):",
                })
                st.rerun()
        else:
            st.warning("QR Code PIX não gerado. Verifique a integração com o Asaas.")

        st.info("⏳ Aguardando confirmação de pagamento automaticamente...")

    _render_payment_polling()


@st.fragment(run_every=5)
def _render_payment_polling() -> None:
    """
    Verifica o status do pagamento a cada 5 s (fragment independente).
    Ao detectar aprovação, atualiza o estado e recarrega a aplicação.
    """
    if st.session_state.get("flow_state") != "aguardando_pagamento_pix":
        return
    if st.session_state.get("fm_payment_confirmed"):
        return
    payment_id = st.session_state.get("fm_payment_id")
    if not payment_id:
        return

    try:
        from database.engine import get_db
        from database.models import Payment, PaymentStatus
        with get_db() as db:
            payment = db.query(Payment).filter_by(id=payment_id).first()
            if payment and payment.status == PaymentStatus.approved:
                st.session_state.fm_payment_confirmed = True
                st.session_state.flow_state = "aguardando_entrega"
                nome  = st.session_state.get("fm_nome_entrega", "")
                end   = st.session_state.get("fm_endereco_entrega", "")
                total = _get_flow_manager().cart_total()
                num   = st.session_state.get("fm_order_number", "")
                st.session_state.fm_messages.append({
                    "role":    "assistant",
                    "content": (
                        f"✅ **Pagamento de R$ {total:.2f} confirmado!** 🎉\n\n"
                        f"Pedido **{num}** em preparação com carinho, {nome}!\n\n"
                        f"📦 Entrega para: {end}"
                    ).replace(".", ",", 1),
                })
                st.rerun(scope="app")
    except Exception:
        pass  # Polling silencioso — tenta no próximo ciclo


def _render_pos_pagamento() -> None:
    """Vídeo de confirmação + status — flow_state: aguardando_entrega."""
    fm    = _get_flow_manager()
    nome  = st.session_state.get("fm_nome_entrega", "")
    end   = st.session_state.get("fm_endereco_entrega", "")
    total = fm.cart_total()
    num   = st.session_state.get("fm_order_number", "")

    with st.container(border=True):
        st.markdown("### 🎉 Pedido Confirmado!")
        st.success(
            f"**Pedido {num}** em preparação! 🍫\n\n"
            f"**Total pago:** R$ {total:.2f}\n\n"
            f"**Entrega para:** {nome} — {end}"
        )

        if not st.session_state.get("fm_video_seen"):
            video_path = _VIDEOS_DIR / "pagamento-confirmado.mp4"
            if video_path.exists():
                st.markdown("---")
                st.markdown("#### 🎬 Uma mensagem especial da Alma de Cacau:")
                cols = st.columns([1, 6, 1])
                with cols[1]:
                    st.video(str(video_path), autoplay=True)
                if st.button("▶ Continuar", key="video_ok"):
                    st.session_state.fm_video_seen = True
                    st.rerun()
        else:
            st.info(
                "Seu pedido está sendo preparado com muito carinho! "
                "Em breve nossa equipe entrará em contato. 🤎"
            )
            if st.button("🍫 Fazer novo pedido", key="novo_pedido", type="primary"):
                fm.reset_flow()
                st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# PROCESSAMENTO DE ENTRADA
# ──────────────────────────────────────────────────────────────────────────────

_NAME_RE = re.compile(
    r"(?:meu nome é|me chamo|sou o|sou a|eu sou)\s+([A-Za-z\u00c0-\u00fa]+)",
    re.IGNORECASE,
)


def _extract_name(text: str) -> None:
    """Tenta extrair o nome do cliente da mensagem."""
    if st.session_state.get("fm_lead_name"):
        return
    m = _NAME_RE.search(text)
    if m:
        st.session_state.fm_lead_name = m.group(1).strip().title()
    elif len(text.strip().split()) <= 3 and re.match(r"^[A-Za-zÀ-ú ]+$", text.strip()):
        st.session_state.fm_lead_name = text.strip().title()


def _process_input(text: str) -> None:
    """
    Processa mensagem do usuário:
    1. Extrai nome, se ainda não coletado.
    2. Registra no histórico fm_messages.
    3. Delega ao CacauFlowManager.
    4. Fallback: classifica intent via LLM.
    5. Se sem resposta estruturada, pede ao Groq.
    """
    fm = _get_flow_manager()
    _extract_name(text)
    st.session_state.fm_messages.append({"role": "user", "content": text})

    state = st.session_state.get("flow_state", "aguardando_intencao")

    # Fallback de intent via LLM para estados conversacionais
    if state in ("aguardando_intencao", "aguardando_adicional"):
        intent = _classify_intent(text)
        if intent.get("intencao_compra") and intent.get("sabor"):
            key = str(intent["sabor"]).lower().strip()
            if key in PRODUCT_MAP:
                fm._set_flavor(key, PRODUCT_MAP[key])
                st.session_state.flow_state = "aguardando_quantidade"
                st.rerun()
                return

    response = fm.handle_user_message(text)
    new_state = st.session_state.get("flow_state", "aguardando_intencao")

    # Estados que usam widget — não precisam de resposta textual adicional
    widget_states = {
        "aguardando_quantidade", "aguardando_confirmacao_total",
        "aguardando_autorizacao_dados", "gerando_pix",
        "aguardando_pagamento_pix", "aguardando_entrega",
    }
    if new_state in widget_states and response is None:
        st.rerun()
        return

    # Geração de resposta textual
    if response is None:
        had_name = st.session_state.get("_had_name_before", False)
        name = st.session_state.get("fm_lead_name")
        if not had_name and name:
            response = (
                f"Prazer, **{name}**! 🍫 Você já tem algum sabor em mente "
                "ou prefere que eu apresente nossos sabores disponíveis?"
            )
            show_img = False  # mensagem de saudacao — sem imagem
        else:
            response = _call_groq()
            show_img = True   # resposta do LLM pode exibir imagens
    else:
        show_img = False      # resposta estruturada do FlowManager — sem imagem

    # Atualiza flag de nome conhecido
    if st.session_state.get("fm_lead_name"):
        st.session_state["_had_name_before"] = True

    if response:
        st.session_state.fm_messages.append({
            "role": "assistant",
            "content": response,
            "skip_images": not show_img,
        })

    st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

def render() -> None:
    """Entry point chamado pelo roteador de páginas."""
    try:
        _render_body()
    except Exception as exc:
        st.error(f"⚠️ Erro no assistente: {exc}")
        if st.toggle("Ver detalhes técnicos", key="toggle_err"):
            st.code(traceback.format_exc())


def _render_body() -> None:
    _init_state()
    st.markdown(_ASSISTANT_CSS, unsafe_allow_html=True)
    st.markdown(_hero_html(), unsafe_allow_html=True)

    # Loop de mensagens
    avatar = _cacau_avatar()
    for msg in st.session_state.fm_messages:
        av = avatar if msg["role"] == "assistant" else ":material/person:"
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])
        # Exibe imagens apenas em mensagens do LLM (skip_images=False) — nunca em erros ou transicoes
        if msg["role"] == "assistant" and not msg.get("skip_images", True):
            _show_product_images(_detect_products_in_text(msg["content"]))

    # Widget do estado atual
    state = st.session_state.get("flow_state", "aguardando_intencao")

    if state == "aguardando_quantidade":
        _render_quantity_widget()
        return

    if state == "aguardando_confirmacao_total":
        _render_order_summary()
        return

    if state == "aguardando_autorizacao_dados":
        _render_lgpd_screen()
        return

    if state == "gerando_pix":
        _render_gerando_pix()
        return

    if state == "aguardando_pagamento_pix":
        _render_pix_panel()
        return

    if state in ("aguardando_entrega", "pedido_finalizado"):
        _render_pos_pagamento()
        return

    # Chat input — estados conversacionais
    placeholder = {
        "coletando_nome_entrega":     "Digite seu nome para entrega...",
        "coletando_endereco_entrega": "Rua, número, bairro, cidade...",
        "coletando_cpf":              "Somente os 11 números do CPF...",
    }.get(state, "Digite sua mensagem para a Cacau... 🍫")

    if prompt := st.chat_input(placeholder, key="cacau_chat_input"):
        _process_input(prompt)
