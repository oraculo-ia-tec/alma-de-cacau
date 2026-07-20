# 🍫 Alma de Cacau

> **Pequenos pedaços de felicidade, transformando chocolate em lembrança.**

Uma experiência digital de vendas para uma marca de bombons e trufas artesanais premium. A **Alma de Cacau** une atendimento conversacional com inteligência artificial, catálogo estruturado, gestão de pedidos e pagamentos via PIX para transformar cada compra em um momento especial.

A protagonista da experiência é a **Cacau**: especialista virtual em bombons artesanais, curadoria de sabores e atendimento de vendas. Ela orienta o cliente com uma comunicação acolhedora, elegante e objetiva, ajudando-o a descobrir, escolher e comprar a trufa ideal.

---

## ✨ O que é a Alma de Cacau?

A Alma de Cacau é uma aplicação de e-commerce conversacional para chocolates artesanais. Em vez de apenas navegar por uma vitrine, o cliente conversa com a Cacau, recebe recomendações, conhece a experiência sensorial de cada trufa e conclui seu pedido em um fluxo guiado.

O projeto foi pensado para unir o cuidado de uma confeitaria artesanal à eficiência de uma operação digital: catálogo centralizado, estoque, clientes, endereços, pedidos, pagamentos e notificações estruturados em banco de dados.

## 🤎 Conheça a Cacau

**Cacau** é a especialista virtual da marca. Ela não é apenas um chatbot: é a consultora de vendas da Alma de Cacau.

- Apresenta exclusivamente o catálogo oficial da marca
- Descreve sabores, experiências sensoriais e sugestões de degustação
- Reconhece intenção de compra e conduz o cliente até a seleção de quantidade
- Respeita restrições e alertas relacionados a amendoim, castanhas e laticínios
- Mantém uma conversa breve, acolhedora, elegante e voltada à conversão
- Ajuda a transformar um pedido em presente, memória e afeto

> *Mais que um bombom, um momento só seu.*

## 🍬 Catálogo oficial

| Trufa artesanal | Experiência | Preço unitário |
|---|---|---:|
| 🌶️ Trufa de Pimenta | Equilíbrio e intensidade | R$ 10,50 |
| 🥜 Trufa Doce de Leite com Amendoim | Pura nostalgia | R$ 9,90 |
| 🌰 Trufa de Castanha | Sofisticação e crocância | R$ 9,50 |
| 🍫 Trufa de Chocolate Branco | Delicadeza em cada mordida | R$ 9,50 |
| 💚 Trufa de Pistache | Refinado e único | R$ 10,50 |
| 🍸 Trufa de Amarula | Cremosidade e charme | R$ 9,90 |
| ☕ Trufa de Café | Energia e sabor | R$ 8,90 |

A marca também oferece Caixa Degustação com 9 unidades e opções de embalagens Standard, Premium e Luxury.

## 🚀 Funcionalidades

- **Atendimento conversacional com IA:** a Cacau utiliza Groq para responder de forma natural e aderente ao catálogo da marca
- **Classificação de intenção:** identifica quando o cliente quer conhecer sabores ou finalizar uma compra
- **Fluxo de pedido guiado:** escolha de sabor, quantidade, identificação do cliente e criação estruturada do pedido
- **Catálogo centralizado:** sabores, produtos, preços, estoque, categorias, ingredientes e alergênicos no banco de dados
- **Pagamentos via Asaas:** criação de cobranças PIX, recuperação de QR Code e código copia-e-cola
- **Gestão de pedidos:** cálculo de totais, baixa de estoque, histórico de status e suporte a entrega ou retirada
- **Gestão de clientes:** perfil, endereços, preferências de sabores, consentimento de marketing e alertas de alergia
- **Notificações:** serviços preparados para comunicação com o cliente e operação administrativa
- **Administração do catálogo:** scripts de seed e sincronização para manter os 7 sabores oficiais consistentes no banco

## 🧩 Arquitetura

```text
Cliente
  │
  ▼
Streamlit (interface e chat da Cacau)
  │
  ├── Groq / LLM ─────────► Atendimento e classificação de intenção
  │
  ├── Serviços de domínio ─► Clientes, pedidos, produtos, pagamentos, notificações
  │
  ├── SQLAlchemy ──────────► SQLite (ambiente atual)
  │
  └── Asaas API ───────────► Clientes, cobranças PIX, QR Code e status de pagamento
```

A aplicação separa interface, serviços de negócio, adaptadores externos e persistência. Essa organização permite evoluir a base para FastAPI, PostgreSQL, webhooks e integrações operacionais sem reescrever o fluxo principal.

## 🛠️ Tecnologias

- **Python**
- **Streamlit** para interface e experiência conversacional
- **SQLAlchemy** para modelagem e persistência de dados
- **SQLite** como banco de dados local atual
- **Pydantic** para validação de entradas e contratos internos
- **Groq** para a inteligência conversacional da Cacau
- **Asaas API v3** para clientes, cobranças e PIX
- **HTTPX** para comunicação com serviços externos

## 📁 Organização do projeto

```text
ALMA-DE-CACAU/
├── app.py                     # Entrada da aplicação Streamlit
├── assistant.py               # Persona e fluxo conversacional da Cacau
├── database/
│   ├── engine.py              # Conexão e inicialização do banco
│   ├── models.py              # Modelos SQLAlchemy
│   ├── seed.py                # Dados iniciais do sistema
│   └── update_catalog.py      # Sincronização dos 7 sabores oficiais
├── services/
│   ├── ai_service.py          # Recomendações e mensagens com IA
│   ├── customer_service.py    # Clientes e endereços
│   ├── order_service.py       # Pedidos, itens e estoque
│   ├── payment_service.py     # Criação, confirmação e estorno de pagamentos
│   ├── product_service.py     # Produtos e catálogo
│   ├── notification_service.py# Notificações
│   └── gift_service.py        # Recursos para presentes
├── adapters/
│   └── asaas_adapter.py       # Integração com a API do Asaas
└── produtos/                  # Imagens dos produtos
```

> Os caminhos podem variar conforme a estrutura final do repositório. Mantenha a separação por responsabilidade ao evoluir o projeto.

## ⚙️ Como executar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/oraculo-ia-tec/alma-de-cacau.git
cd alma-de-cacau
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
```

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto. Nunca envie esse arquivo para o GitHub.

```env
GROQ_API_KEY=sua_chave_groq
GROQ_MODEL=llama-3.3-70b-versatile

ASAAS_API_KEY=sua_chave_asaas
ASAAS_ENV=sandbox

DATABASE_URL=sqlite:///./alma_de_cacau.db
```

### 5. Inicialize o banco e o catálogo

```bash
python -c "from database.seed import run_seed; run_seed()"
```

Para sincronizar ou corrigir especificamente os 7 produtos oficiais:

```bash
python -c "from database.update_catalog import run_update; run_update()"
```

### 6. Execute a aplicação

```bash
streamlit run app.py
```

Abra o endereço exibido pelo Streamlit no navegador.

## 💳 Fluxo de compra

1. O visitante inicia uma conversa com a Cacau
2. A Cacau coleta o nome e entende a intenção do cliente
3. O cliente conhece os sabores ou informa sua escolha
4. A aplicação apresenta a trufa e permite selecionar a quantidade
5. Os dados necessários para pedido e entrega são coletados
6. O pedido é gravado, o estoque é atualizado e a cobrança PIX é criada no Asaas
7. O QR Code PIX e o código copia-e-cola são apresentados ao cliente
8. A confirmação de pagamento atualiza a operação para produção e entrega

## 🔐 Boas práticas de segurança

- Nunca publique `GROQ_API_KEY`, `ASAAS_API_KEY`, senhas ou dados de clientes
- Mantenha `.env`, bancos locais `*.db` e ambientes virtuais fora do versionamento
- Armazene CPF somente de forma protegida; o modelo prevê hash para o CPF do perfil de cliente
- Valide webhooks do provedor de pagamentos antes de alterar o status financeiro de um pedido
- Use o ambiente `sandbox` do Asaas durante desenvolvimento e testes

Exemplo de `.gitignore`:

```gitignore
venv/
.env
*.db
__pycache__/
.streamlit/secrets.toml
```

## 🗺️ Próximos passos

- [ ] Exibir QR Code e código PIX imediatamente após criar a cobrança
- [ ] Criar endpoint FastAPI seguro para webhook do Asaas
- [ ] Atualizar pagamento e pedido automaticamente com eventos `PAYMENT_CONFIRMED` e `PAYMENT_RECEIVED`
- [ ] Mostrar confirmação de pagamento no chat com `st.dialog`
- [ ] Enviar e-mail operacional ao administrador com dados do pedido confirmado
- [ ] Migrar SQLite para PostgreSQL no ambiente de produção
- [ ] Criar painel administrativo para catálogo, estoque, pedidos e produção
- [ ] Adicionar testes automatizados para pedido, pagamento e webhook
- [ ] Organizar novas capacidades em uma pasta `skills/`

## 🤝 Contribuição

Contribuições são bem-vindas. Para colaborar:

1. Crie uma branch com um nome descritivo
2. Faça alterações pequenas e focadas
3. Teste o fluxo afetado localmente
4. Abra um Pull Request explicando o contexto, a solução e como validar

## 📄 Licença

Defina a licença do projeto antes de disponibilizá-lo publicamente. Uma opção comum para projetos open source é a licença MIT.

---

<p align="center">
  Feito com carinho, tecnologia e muito cacau. 🍫<br>
  <strong>Alma de Cacau — transformando chocolate em lembrança.</strong>
</p>
