"""
Motor de fluxo conversacional — Alma de Cacau
Implementa o fluxo guiado do FLUXO_CONVERSACIONAL.md adaptado para
trufas artesanais (7 sabores) adaptado de fluxo original guiado.

Estados do fluxo (flow_state):
    aguardando_intencao        → estado inicial
    aguardando_sabor           → exibe catálogo, aguarda escolha
    aguardando_quantidade      → widget de quantidade renderizado
    aguardando_adicional       → após adicionar item, pergunta se quer mais
    aguardando_confirmacao_total → resumo do pedido, aguarda confirmação
    aguardando_autorizacao_dados → tela de consentimento LGPD
    coletando_nome_entrega     → coleta nome via chat
    coletando_endereco_entrega → coleta endereço via chat
    coletando_cpf              → coleta CPF via chat
    gerando_pix                → gera cobrança no Asaas
    aguardando_pagamento_pix   → QR Code + polling de confirmação
    aguardando_entrega         → pagamento confirmado, em preparo/entrega
    pedido_finalizado          → encerrado
"""
from __future__ import annotations

import re
from typing import Optional
import streamlit as st


# ──────────────────────────────────────────────────────────────────────────────
# CATÁLOGO OFICIAL — 7 SABORES
# ──────────────────────────────────────────────────────────────────────────────

PRODUCT_MAP: dict[str, dict] = {
    "pimenta": {
        "label": "Trufa de Pimenta",
        "sku": "ADC-PIM",
        "price": 10.50,
        "price_str": "R$ 10,50",
        "file": "pimenta.png",
        "experiencia": "Equilíbrio e intensidade",
        "descricao": "O contraste perfeito entre o doce e o picante.",
        "degustacao": "Aprecie devagar, sentindo o calor suave.",
    },
    "doce de leite": {
        "label": "Trufa Doce de Leite com Amendoim",
        "sku": "ADC-DLA",
        "price": 9.90,
        "price_str": "R$ 9,90",
        "file": "doce-de-leite-com-amendoim.png",
        "experiencia": "Pura nostalgia",
        "descricao": "Doce de leite cremoso com a crocância do amendoim.",
        "degustacao": "Ideal com um café.",
    },
    "castanha": {
        "label": "Trufa de Castanha",
        "sku": "ADC-CAS",
        "price": 9.50,
        "price_str": "R$ 9,50",
        "file": "castanha.png",
        "experiencia": "Sofisticação e crocância",
        "descricao": "Recheio cremoso com pedaços selecionados de castanha.",
        "degustacao": "Harmoniza com um bom vinho.",
    },
    "chocolate branco": {
        "label": "Trufa de Chocolate Branco",
        "sku": "ADC-CBR",
        "price": 9.50,
        "price_str": "R$ 9,50",
        "file": "chocolate-branco.png",
        "experiencia": "Delicadeza em cada mordida",
        "descricao": "Cremoso, suave e irresistível.",
        "degustacao": "Aprecie com calma.",
    },
    "pistache": {
        "label": "Trufa de Pistache",
        "sku": "ADC-PIS",
        "price": 10.50,
        "price_str": "R$ 10,50",
        "file": "pistache.png",
        "experiencia": "Refinado e único",
        "descricao": "Sabor nobre, cremoso e levemente amanteigado.",
        "degustacao": "Deguste lentamente.",
    },
    "amarula": {
        "label": "Trufa de Amarula",
        "sku": "ADC-AMA",
        "price": 9.90,
        "price_str": "R$ 9,90",
        "file": "amarula.png",
        "experiencia": "Cremosidade e charme",
        "descricao": "Toque suave e marcante do licor Amarula.",
        "degustacao": "Sirva geladinho.",
    },
    "cafe": {
        "label": "Trufa de Cafe",  # sem acento: coincide com seed (ADC-CAF)
        "sku": "ADC-CAF",
        "price": 8.90,
        "price_str": "R$ 8,90",
        "file": "cafe.png",
        "experiencia": "Energia e sabor",
        "descricao": "Recheio intenso que desperta os sentidos.",
        "degustacao": "Companheiro ideal para o café da manhã.",
    },
}
# Aliases de detecção (não exibidos na listagem)
PRODUCT_MAP["café"]       = PRODUCT_MAP["cafe"]
PRODUCT_MAP["amendoim"]   = PRODUCT_MAP["doce de leite"]
PRODUCT_MAP["branco"]     = PRODUCT_MAP["chocolate branco"]
PRODUCT_MAP["choco branco"] = PRODUCT_MAP["chocolate branco"]
PRODUCT_MAP["pistachio"]  = PRODUCT_MAP["pistache"]
PRODUCT_MAP["caramelo"]   = PRODUCT_MAP["doce de leite"]  # variação comum


# ──────────────────────────────────────────────────────────────────────────────
# VOCABULÁRIO DE INTENÇÃO
# ──────────────────────────────────────────────────────────────────────────────

_GREETINGS = frozenset({
    "oi", "olá", "ola", "hey", "e aí", "eae", "bom dia",
    "boa tarde", "boa noite", "tudo bem", "opa", "salve", "hello",
})
_FINALIZE = frozenset({
    "finalizar", "fechar", "encerrar", "só isso", "so isso",
    "nada mais", "é isso", "e isso", "pode fechar", "já está",
    "ja esta", "tchau", "pronto", "terminei", "acabou",
})
# NOTA: "não" e "nao" removidos de _FINALIZE para evitar ambiguidade
# com "não quero esse sabor" — verificação feita com contexto em _handle_adicional

_FINALIZE_SHORT = frozenset({"não", "nao"})  # Apenas se for resposta isolada
_BUY = frozenset({
    "quero", "queria", "gostaria", "preciso", "comprar",
    "levar", "vou", "manda", "escolhi", "pode", "fechou", "sim",
})
_SHOW_CATALOG = frozenset({
    "sabor", "sabores", "opção", "opcao", "opções", "opcoes",
    "ver", "mostrar", "conhecer", "cardapio", "menu",
    "catalogo", "catálogo", "lista", "quais", "qual",
})


# ──────────────────────────────────────────────────────────────────────────────
# VALORES PADRÃO DE ESTADO
# Prefixo "fm_" isola chaves do flow_manager do restante do session_state
# ──────────────────────────────────────────────────────────────────────────────

FLOW_STATE_DEFAULTS: dict = {
    "flow_state":            "aguardando_intencao",
    "fm_cart":               [],
    "fm_flavor_key":         None,   # sabor selecionado aguardando quantidade
    "fm_flavor_info":        None,
    "fm_nome_entrega":       None,
    "fm_endereco_entrega":   None,
    "fm_cpf":                None,
    "fm_messages":           [],
    "fm_chat_started":       False,
    "fm_pix_result":         None,   # dict com encodedImage + payload
    "fm_payment_id":         None,   # id interno (DB) do Payment
    "fm_payment_confirmed":  False,
    "fm_order_number":       None,
    "fm_customer_profile_id": None,
}


# ──────────────────────────────────────────────────────────────────────────────
# FLOW MANAGER
# ──────────────────────────────────────────────────────────────────────────────

class CacauFlowManager:
    """
    Gerencia os estados do chat de vendas da Alma de Cacau.

    Uso típico em render():
        fm = _get_flow_manager()   # cached via st.cache_resource
        fm.init_state()
        response = fm.handle_user_message(user_text)
    """

    # ── Inicialização ─────────────────────────────────────────────────────
    def init_state(self) -> None:
        """Garante que todos os defaults de estado estão no session_state."""
        for key, val in FLOW_STATE_DEFAULTS.items():
            if key not in st.session_state:
                # Copia listas para evitar referências compartilhadas
                st.session_state[key] = list(val) if isinstance(val, list) else val

    # ── Dispatcher principal ──────────────────────────────────────────────
    def handle_user_message(self, text: str) -> Optional[str]:
        """
        Processa a mensagem conforme o flow_state atual.
        Retorna texto de resposta da assistente, ou None para delegar ao LLM.
        """
        state: str = st.session_state.get("flow_state", "aguardando_intencao")
        dispatch = {
            "aguardando_intencao":          self._handle_intencao,
            "aguardando_sabor":             self._handle_sabor,
            "aguardando_adicional":         self._handle_adicional,
            "aguardando_confirmacao_total": lambda _: None,  # widget controla
            "coletando_nome_entrega":       self._handle_nome,
            "coletando_endereco_entrega":   self._handle_endereco,
            "coletando_cpf":               self._handle_cpf,
        }
        handler = dispatch.get(state)
        return handler(text) if handler else None

    # ── Handlers por estado ───────────────────────────────────────────────
    def _handle_intencao(self, text: str) -> Optional[str]:
        lower = text.lower().strip()
        words = set(re.sub(r"[,!?.]", "", lower).split())

        # Saudação pura → LLM responde sem mudar estado
        if words and words.issubset(_GREETINGS):
            return None

        # Sabor detectado diretamente
        key, info = self._detect_flavor(lower)
        if key:
            self._set_flavor(key, info)
            st.session_state.flow_state = "aguardando_quantidade"
            return None  # widget de quantidade renderiza

        # Quer ver catálogo ou inicia compra
        if (_SHOW_CATALOG | _BUY) & words:
            st.session_state.flow_state = "aguardando_sabor"
            return self.flavor_list_msg()

        return None  # LLM responde

    def _handle_sabor(self, text: str) -> Optional[str]:
        key, info = self._detect_flavor(text.lower())
        if key:
            self._set_flavor(key, info)
            st.session_state.flow_state = "aguardando_quantidade"
            return None
        return (
            "Não encontrei esse sabor 😊 Por favor, escolha um dos nossos:\n\n"
            + self.flavor_list_msg()
        )

    def _handle_adicional(self, text: str) -> Optional[str]:
        lower = text.lower().strip()
        words = set(re.sub(r"[,!?.]", "", lower).split())

        # Quer finalizar — verificações com contexto para evitar falsos positivos
        # 1. Expressões claras de finalização
        if any(w in lower for w in _FINALIZE):
            if not st.session_state.fm_cart:
                return "Seu carrinho está vazio. O que você gostaria de comprar? 🍫"
            st.session_state.flow_state = "aguardando_confirmacao_total"
            return None  # widget de resumo renderiza

        # 2. "não" / "nao" isolado (sem outras palavras significativas)
        if words and words.issubset(_FINALIZE_SHORT | {"obrigado", "obrigada", "vlw", "valeu"}):
            if not st.session_state.fm_cart:
                return "Seu carrinho está vazio. O que você gostaria de comprar? 🍫"
            st.session_state.flow_state = "aguardando_confirmacao_total"
            return None

        # Novo sabor detectado
        key, info = self._detect_flavor(lower)
        if key:
            self._set_flavor(key, info)
            st.session_state.flow_state = "aguardando_quantidade"
            return None

        # Quer adicionar mais, mas não especificou
        if any(w in lower for w in {"sim", "mais", "outro", "outra", "quero mais", "adicionar"}):
            st.session_state.flow_state = "aguardando_sabor"
            return self.flavor_list_msg()

        return None  # LLM responde

    def _handle_nome(self, text: str) -> Optional[str]:
        name = text.strip()
        if len(name) < 2:
            return "Por favor, informe um nome válido para a entrega. 😊"
        st.session_state.fm_nome_entrega = name
        st.session_state.flow_state = "coletando_endereco_entrega"
        return "📍 Qual o endereço de entrega?\n_(Rua, número, bairro, cidade)_"

    def _handle_endereco(self, text: str) -> Optional[str]:
        addr = text.strip()
        if len(addr) < 5:
            return "Por favor, informe o endereço completo — Rua, número, bairro, cidade. 📍"
        st.session_state.fm_endereco_entrega = addr
        st.session_state.flow_state = "coletando_cpf"
        return "🔒 Digite seu **CPF** (somente 11 números, sem pontos ou traços):"

    def _handle_cpf(self, text: str) -> Optional[str]:
        digits = re.sub(r"\D", "", text)
        if len(digits) not in (11, 14):
            return (
                "CPF inválido. Por favor, digite somente os 11 números do CPF, "
                "sem pontos ou traços. 🔒"
            )
        st.session_state.fm_cpf = digits
        st.session_state.flow_state = "gerando_pix"
        return "⏳ Aguarde um instante enquanto preparo seu PIX..."

    # ── Carrinho ──────────────────────────────────────────────────────────
    def add_to_cart(self, flavor_key: str, flavor_info: dict, qty: int) -> None:
        """Adiciona item ou incrementa quantidade se já existir no carrinho."""
        sku = flavor_info.get("sku", "")
        for item in st.session_state.fm_cart:
            if item.get("sku") == sku or item["label"] == flavor_info["label"]:
                item["quantity"] += qty
                item["subtotal"] = round(item["unit_price"] * item["quantity"], 2)
                return
        st.session_state.fm_cart.append({
            "flavor_key": flavor_key,
            "label":      flavor_info["label"],
            "sku":        sku,
            "unit_price": flavor_info["price"],
            "quantity":   qty,
            "subtotal":   round(flavor_info["price"] * qty, 2),
            "file":       flavor_info.get("file", ""),
        })

    def cart_total(self) -> float:
        return round(sum(i["subtotal"] for i in st.session_state.fm_cart), 2)

    # ── Helpers ───────────────────────────────────────────────────────────
    def _detect_flavor(self, text_lower: str) -> tuple[Optional[str], Optional[dict]]:
        for key, info in PRODUCT_MAP.items():
            if key in text_lower:
                return key, info
        return None, None

    def _set_flavor(self, key: str, info: dict) -> None:
        st.session_state.fm_flavor_key  = key
        st.session_state.fm_flavor_info = info

    def flavor_list_msg(self) -> str:
        """Retorna mensagem formatada com os 7 sabores disponíveis."""
        lines = ["🍫 **Nossos 7 sabores artesanais:**\n"]
        seen: set[str] = set()
        for info in PRODUCT_MAP.values():
            lbl = info["label"]
            if lbl not in seen:
                seen.add(lbl)
                lines.append(f"• **{lbl}** — {info['price_str']}")
                lines.append(f"  _{info['experiencia']}_")
        lines.append("\nQual sabor te interessa? 😊")
        return "\n".join(lines)

    def reset_flow(self) -> None:
        """Reinicia o fluxo mantendo os dados do usuário logado."""
        for key, val in FLOW_STATE_DEFAULTS.items():
            st.session_state[key] = list(val) if isinstance(val, list) else val
