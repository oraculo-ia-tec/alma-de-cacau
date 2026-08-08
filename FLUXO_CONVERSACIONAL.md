# Documento Técnico: Fluxo de Conversação — Alma de Cacau

**Versão:** 3.0  
**Data:** 08/08/2026  
**Projeto:** Alma de Cacau — Trufas e Bombons Artesanais  
**Stack:** Python 3.x · Streamlit · Groq (Llama 3.3-70b) · ASAAS API · SQLAlchemy (SQLite)

---

## Sumário

1. [Inicialização da Aplicação](#1-inicialização-da-aplicação)
2. [Autenticação do Usuário](#2-autenticação-do-usuário)
3. [Entrada no Assistente de Vendas](#3-entrada-no-assistente-de-vendas)
4. [Motor de Fluxo Conversacional — Estados](#4-motor-de-fluxo-conversacional--estados)
5. [Seleção de Produtos — Subfluxos](#5-seleção-de-produtos--subfluxos)
6. [Carrinho e Confirmação do Total](#6-carrinho-e-confirmação-do-total)
7. [Coleta de Dados para Entrega](#7-coleta-de-dados-para-entrega)
8. [Geração do PIX (ASAAS API)](#8-geração-do-pix-asaas-api)
9. [Polling de Confirmação de Pagamento](#9-polling-de-confirmação-de-pagamento)
10. [Skill: Vídeo de Confirmação](#10-skill-vídeo-de-confirmação)
11. [Mapa de Estados (flow_state)](#11-mapa-de-estados-flow_state)
12. [Arquivos por Responsabilidade](#12-arquivos-por-responsabilidade)
13. [Catálogo Oficial — 7 Sabores](#13-catálogo-oficial--7-sabores)

---

## 1. Inicialização da Aplicação

**Arquivo:** `app.py`

```
Streamlit inicia
    │
    ├─ @st.cache_resource → _boot_db()
    │       └─ init_db() + run_seed()
    │               ├─ create_tables()        ← Cria schema SQLAlchemy se não existe
    │               └─ seed_all()             ← Popula produtos, usuários
    │
    ├─ load_dotenv()                          ← Carrega .env (ASAAS_API_KEY, GROQ_API_KEY, etc.)
    │
    ├─ st.set_page_config(...)
    │
    ├─ inject_css() + init_state()            ← CSS global e estado inicial
    │
    └─ _sidebar_nav() + _render_page()        ← Navegação e roteamento de páginas
```

**Configurações carregadas do `.env`:**

| Variável | Uso |
|---|---|
| `ASAAS_API_KEY` | Autenticação API de pagamentos PIX |
| `GROQ_API_KEY` | LLM Llama 3.3-70b para chat conversacional |
| `DATABASE_URL` | `sqlite:///alma_cacau.db` |
| `EMAIL_*` | SMTP para notificações |

---

## 2. Autenticação do Usuário

**Arquivo:** `app.py` → `services/customer_service.py`

```
Sidebar renderiza formulário de login
    │
    ├─ Usuário preenche email + senha
    │
    └─ _do_login(email, password)
            │
            └─ CustomerService.authenticate()
                    ├─ Query: User.email == email
                    └─ bcrypt.checkpw(password, password_hash)
                    │
                    └─ Se autenticado → session_state:
                            user_id = user.id
                            customer_name = user.full_name
                            customer_email = user.email
                            is_admin = (role == "admin")
                            customer_id = profile.id
```

---

## 3. Entrada no Assistente de Vendas

**Arquivo:** `frontend/pages/customer/assistant.py` → `render()`

```
Usuário navega para /assistant (padrão)
    │
    ├─ _init_state()
    │       └─ CacauFlowManager().init_state()
    │               └─ Defaults: flow_state="aguardando_intencao", fm_cart=[], fm_messages=[], etc.
    │
    ├─ Mensagem inicial da Cacau:
    │       "Olá! Seja muito bem-vindo(a) à Alma de Cacau! 🍫
    │        Sou a Cacau, sua assistente de chocolates artesanais.
    │        Antes de te apresentar nossos bombons, como posso te chamar?"
    │
    └─ Loop de mensagens + widgets por estado
```

---

## 4. Motor de Fluxo Conversacional — Estados

**Arquivo:** `services/flow_manager.py` → `CacauFlowManager.handle_user_message(text)`

Cada mensagem digitada passa pelo dispatcher de estados:

```
handle_user_message(text)
    │
    └─ Dispatcher (switch por flow_state):
            "aguardando_intencao"           → _handle_intencao()
            "aguardando_sabor"              → _handle_sabor()
            "aguardando_adicional"          → _handle_adicional()
            "aguardando_confirmacao_total"  → widget controla
            "coletando_nome_entrega"        → _handle_nome()
            "coletando_endereco_entrega"    → _handle_endereco()
            "coletando_cpf"                 → _handle_cpf()

            # Estados controlados por widget/polling:
            "aguardando_quantidade"         → widget de quantidade
            "aguardando_autorizacao_dados"  → tela LGPD
            "gerando_pix"                   → spinner + API ASAAS
            "aguardando_pagamento_pix"      → QR Code + polling
            "aguardando_entrega"            → vídeo + confirmação
```

---

## 5. Seleção de Produtos — Subfluxos

### 5.1 Intenção Inicial (`aguardando_intencao`)

```
Usuário digita → _handle_intencao(text)
    │
    ├─ É saudação pura? ("oi", "olá", "bom dia"...)
    │       └─ LLM responde, sem mudar estado
    │
    ├─ Detectou sabor diretamente? ("quero pistache", "trufa de amarula")
    │       └─ flow_state = "aguardando_quantidade"
    │          Widget de quantidade renderiza
    │
    ├─ Quer ver catálogo? ("ver sabores", "quais opções", "mostrar")
    │       └─ flow_state = "aguardando_sabor"
    │          Lista os 7 sabores disponíveis
    │
    └─ Outra mensagem
            └─ LLM responde (Groq/Llama)
```

### 5.2 Escolha de Sabor (`aguardando_sabor`)

```
Usuário digita nome do sabor
    │
_handle_sabor(text)
    ├─ Encontrou sabor? (detect_flavor)
    │       └─ flow_state = "aguardando_quantidade"
    │
    └─ Não encontrou?
            └─ "Não encontrei esse sabor 😊 Por favor, escolha um dos nossos:"
               + lista dos 7 sabores novamente
```

### 5.3 Widget de Quantidade (`aguardando_quantidade`)

```
_render_quantity_widget()  ← widget Streamlit
    │
    ├─ Exibe imagem do produto
    ├─ Exibe: nome, preço, experiência, descrição, dica de degustação
    ├─ st.number_input(min=1, max=50, step=1)
    ├─ Subtotal em tempo real
    │
    ├─ [✅ Adicionar ao pedido]
    │       └─ add_to_cart(flavor_key, info, qty)
    │          flow_state = "aguardando_adicional"
    │          Mensagem: "Adicionei X× {sabor} ao pedido! 🎉"
    │
    └─ [↩️ Voltar ao chat]
            └─ flow_state = "aguardando_sabor"
```

---

## 6. Carrinho e Confirmação do Total

### 6.1 Adicional (`aguardando_adicional`)

```
_handle_adicional(text)
    │
    ├─ Quer finalizar? ("finalizar", "fechar", "só isso", "é isso")
    │       └─ Se carrinho vazio: "Seu carrinho está vazio..."
    │          Senão: flow_state = "aguardando_confirmacao_total"
    │
    ├─ Novo sabor detectado?
    │       └─ flow_state = "aguardando_quantidade"
    │
    └─ Quer mais? ("sim", "mais", "outro")
            └─ flow_state = "aguardando_sabor"
               Lista sabores novamente
```

### 6.2 Resumo do Pedido (`aguardando_confirmacao_total`)

```
_render_order_summary()  ← widget Streamlit
    │
    ├─ Lista: item × quantidade → subtotal
    ├─ TOTAL destacado
    │
    ├─ [➕ Adicionar mais]
    │       └─ flow_state = "aguardando_adicional"
    │
    └─ [✅ Confirmar pedido]
            └─ flow_state = "aguardando_autorizacao_dados"
```

---

## 7. Coleta de Dados para Entrega

### 7.1 Autorização de Dados (`aguardando_autorizacao_dados`)

```
_render_lgpd_screen()  ← widget Streamlit
    │
    ├─ Apresenta: dados que serão coletados (nome, endereço, CPF)
    ├─ Nota LGPD
    │
    ├─ [✅ EU CONFIRMO]
    │       └─ flow_state = "coletando_nome_entrega"
    │
    └─ [❌ Cancelar]
            └─ flow_state = "aguardando_confirmacao_total"
```

### 7.2 Nome de Entrega (`coletando_nome_entrega`)

```
_handle_nome(text)
    └─ fm_nome_entrega = text.strip()
       flow_state = "coletando_endereco_entrega"
       "📍 Qual o endereço de entrega?"
```

### 7.3 Endereço de Entrega (`coletando_endereco_entrega`)

```
_handle_endereco(text)
    └─ fm_endereco_entrega = text.strip()
       flow_state = "coletando_cpf"
       "🔒 Digite seu CPF (somente 11 números):"
```

### 7.4 Coleta de CPF (`coletando_cpf`)

```
_handle_cpf(text)
    │
    ├─ Remove não-dígitos
    ├─ len ≠ 11 e ≠ 14?
    │       └─ "CPF inválido..."
    │
    └─ Válido:
            fm_cpf = digits
            flow_state = "gerando_pix"
            "⏳ Aguarde enquanto preparo seu PIX..."
```

---

## 8. Geração do PIX (ASAAS API)

**Arquivo:** `frontend/pages/customer/assistant.py` → `_render_gerando_pix()` + `_build_pix_payment()`

```
_render_gerando_pix()
    │
    ├─ st.spinner("Preparando seu PIX com segurança...")
    │
    └─ _build_pix_payment()
            │
            ├─ asaas_create_customer(name, cpf, email)
            │       └─ POST /customers
            │
            ├─ CustomerService.register() se não existe
            │
            ├─ CustomerService.add_address()
            │
            ├─ OrderService.create_order()
            │
            ├─ PaymentService.create_payment(method=PIX)
            │
            └─ PaymentService.get_pix_qr_code()
                    └─ GET /payments/{id}/pixQrCode
                            └─ Retorna: encodedImage (base64), payload

    Resultado:
        fm_pix_result = {encodedImage, payload}
        fm_payment_id = payment.id
        fm_order_number = order.order_number
        flow_state = "aguardando_pagamento_pix"
```

---

## 9. Polling de Confirmação de Pagamento

**Arquivo:** `frontend/pages/customer/assistant.py` → `@st.fragment(run_every=5) _render_payment_polling()`

```
_render_payment_polling()  ← @st.fragment(run_every=5)
    │
    ├─ flow_state ≠ "aguardando_pagamento_pix"? → return
    ├─ fm_payment_confirmed == True? → return
    ├─ fm_payment_id ausente? → return
    │
    └─ Query Payment.status
            │
            ├─ status == "approved":
            │       fm_payment_confirmed = True
            │       flow_state = "aguardando_entrega"
            │       Mensagem: "✅ Pagamento confirmado! 🎉"
            │       st.rerun(scope="app")
            │
            └─ Outro status → aguarda próximo ciclo (5s)
```

---

## 10. Skill: Vídeo de Confirmação

**Arquivo:** `frontend/pages/customer/assistant.py` → `_render_pos_pagamento()`

```
_render_pos_pagamento()
    │
    ├─ Exibe: "🎉 Pedido Confirmado!"
    ├─ Dados: número, total, nome, endereço
    │
    ├─ fm_video_seen == False?
    │       └─ st.video("cacau/videos/pagamento-confirmado.mp4", autoplay=True)
    │          [▶ Continuar] → fm_video_seen = True
    │
    └─ fm_video_seen == True?
            └─ "Seu pedido está sendo preparado..."
               [🍫 Fazer novo pedido] → reset_flow()
```

---

## 11. Mapa de Estados (`flow_state`)

Diagrama completo de transição de estados do `CacauFlowManager`:

```
                    ┌─────────────────────┐
                    │  aguardando_intencao │ ◄── Estado inicial
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
   ┌───────────────────┐              ┌──────────────────────┐
   │  aguardando_sabor │              │ aguardando_quantidade│
   │  (lista sabores)  │              │ (widget numérico)    │
   └─────────┬─────────┘              └──────────┬───────────┘
             │                                    │
             └───────────┬────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ aguardando_adicional │
              └──────────┬───────────┘
                         │ "finalizar" / "só isso"
                         ▼
              ┌───────────────────────────┐
              │ aguardando_confirmacao    │ ◄── Widget resumo
              │ _total                    │
              └────────────┬──────────────┘
                           │ [Confirmar pedido]
                           ▼
              ┌───────────────────────────┐
              │ aguardando_autorizacao    │ ◄── Tela LGPD
              │ _dados                    │
              └────────────┬──────────────┘
                           │ [EU CONFIRMO]
                           ▼
              ┌───────────────────────────┐
              │ coletando_nome_entrega    │
              └────────────┬──────────────┘
                           │
                           ▼
              ┌───────────────────────────┐
              │ coletando_endereco_entrega│
              └────────────┬──────────────┘
                           │
                           ▼
              ┌───────────────────────────┐
              │ coletando_cpf             │
              └────────────┬──────────────┘
                           │ CPF válido
                           ▼
              ┌───────────────────────────┐
              │ gerando_pix               │ ◄── API ASAAS
              └────────────┬──────────────┘
                           │ PIX gerado
                           ▼
              ┌───────────────────────────┐
              │ aguardando_pagamento_pix  │ ◄── QR Code + polling
              └────────────┬──────────────┘
                           │ Pagamento confirmado
                           ▼
              ┌───────────────────────────┐
              │ aguardando_entrega        │ ◄── Vídeo + status
              └───────────────────────────┘
```

---

## 12. Arquivos por Responsabilidade

| Responsabilidade | Arquivo Principal | Descrição |
|---|---|---|
| **Entry point / Auth / Routing** | `app.py` | Inicialização, sidebar, login, roteamento |
| **Motor de fluxo conversacional** | `services/flow_manager.py` | `CacauFlowManager` + PRODUCT_MAP |
| **Interface do assistente** | `frontend/pages/customer/assistant.py` | UI, widgets, polling, vídeo |
| **Serviço de clientes** | `services/customer_service.py` | Autenticação, cadastro, endereços |
| **Serviço de pedidos** | `services/order_service.py` | Criação e gestão de pedidos |
| **Serviço de pagamentos** | `services/payment_service.py` | PIX, QR Code, status |
| **Adaptador ASAAS** | `adapters/asaas_adapter.py` | Cliente HTTP ASAAS |
| **Banco de dados** | `database/engine.py` + `models.py` | SQLAlchemy, modelos |
| **Estado global** | `frontend/state.py` | Session state helpers |
| **Estilo CSS** | `frontend/style.py` | Injeção de CSS |

---

## 13. Catálogo Oficial — 7 Sabores

**Fonte canônica:** `services/flow_manager.py` → `PRODUCT_MAP`

| Sabor | SKU | Preço | Experiência |
|---|---|---|---|
| Trufa de Pimenta | ADC-PIM | R$ 10,50 | Equilíbrio e intensidade |
| Trufa Doce de Leite com Amendoim | ADC-DLA | R$ 9,90 | Pura nostalgia |
| Trufa de Castanha | ADC-CAS | R$ 9,50 | Sofisticação e crocância |
| Trufa de Chocolate Branco | ADC-CBR | R$ 9,50 | Delicadeza em cada mordida |
| Trufa de Pistache | ADC-PIS | R$ 10,50 | Refinado e único |
| Trufa de Amarula | ADC-AMA | R$ 9,90 | Cremosidade e charme |
| Trufa de Cafe | ADC-CAF | R$ 8,90 | Energia e sabor |

**Aliases de detecção:**
- "café" → "cafe"
- "amendoim" → "doce de leite"

---

## ⚠️ Arquivos DEPRECATED (não usar)

Os seguintes arquivos na raiz são **legados** do projeto anterior (Chef Delivery)
e **NÃO** devem ser usados:

| Arquivo | Descrição | Status |
|---|---|---|
| `pedido.py` | Fluxo antigo de carnes | ❌ DEPRECATED |
| `pedido_chat_asaas.py` | Chat antigo com ASAAS | ❌ DEPRECATED |
| `pedido_chat_mcp.py` | Chat antigo com MCP | ❌ DEPRECATED |
| `pedido_integrado.py` | Integração antiga | ❌ DEPRECATED |

O fluxo atual usa **exclusivamente**:
- `frontend/pages/customer/assistant.py`
- `services/flow_manager.py` → `CacauFlowManager`
