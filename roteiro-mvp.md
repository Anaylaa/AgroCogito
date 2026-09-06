# Guia Prático de Implementação: AgroCogito MVP
*Customizado para n8n, SQL, Python e ETL (Mentalidade Pentaho)*

Este roteiro foi desenhado sob medida para o seu perfil técnico. Utilizaremos o **Python** para resolver a lógica matemática complexa, o **SQL** para garantir persistência estruturada e auditabilidade, o **n8n** para a orquestração dos dados e controle do fluxo diário (como faria com o Pentaho, mas com a agilidade de um orquestrador web moderno) e o **Streamlit** (uma biblioteca Python fantástica) para criar a interface web do usuário e o simulador interativo de forma extremamente rápida.

---

## 1. O Coração: O Motor de Recomendação (Python)
A lógica matemática, as validações de dados e as regras de arredondamento (`ceil`/`floor`) foram centralizadas em uma única função puramente determinística.

*   **Fórmulas Utilizadas**:
    *   **Preço Efetivo Futuro**: $Preço\ Futuro + Base\ Esperada - Custo\ Operacional$
    *   **Cenário de Risco de Base (Inferior/Central/Superior)**:
        *   *Inferior*: $Preço\ Futuro + Base\ Esperada - Risco\ de\ Base - Custo\ Operacional$
        *   *Central*: $Preço\ Futuro + Base\ Esperada - Custo\ Operacional$
        *   *Superior*: $Preço\ Futuro + Base\ Esperada + Risco\ de\ Base - Custo\ Operacional$
    *   **Sacas Necessárias (Spot)**: $ceil(Necessidade\ Financeira / Preço\ Spot)$
    *   **Contratos de Hedge Necessários**: $ceil(Quantidade\ Alvo\ Sacas / 450)$ (arredondado para contratos inteiros de $450$ sacas, garantindo que o volume total de hedge $\le$ Produção Disponível).

O motor já foi codificado em Python e valida todos os cenários do produtor padrão da especificação.

---

## 2. A Persistência: Estrutura de Banco de Dados (SQL)
Para armazenar as análises diárias de forma auditável e histórica (garantindo que alterações futuras nas cotações não recalculem o passado), utilizaremos o **SQLite** (ou qualquer banco relacional com o qual você tenha familiaridade).

Aqui está o esquema SQL DDL ideal para o MVP, separando a **análise consolidada** de seus **detalhes históricos** (cotações utilizadas e recomendações geradas):

```sql
-- 1. Tabela Principal de Análises
CREATE TABLE IF NOT EXISTS analyses (
    analysis_id TEXT PRIMARY KEY,          -- Ex: AN-20260817-PROD-001
    producer_id TEXT NOT NULL,             -- Ex: PROD-001
    producer_name TEXT NOT NULL,
    commodity TEXT NOT NULL,               -- Ex: CORN
    generated_at TEXT NOT NULL,            -- ISO8601 Timestamp
    status TEXT NOT NULL,                  -- OPPORTUNITY, WAIT, PARTIAL, etc.
    coe_per_bag REAL NOT NULL,
    cot_per_bag REAL NOT NULL,
    ct_per_bag REAL NOT NULL,
    break_even_per_bag REAL NOT NULL,
    spot_price REAL,                       -- Preço CEPEA na data
    spot_ref_date TEXT,                    -- Data de referência do CEPEA
    best_future_symbol TEXT,
    best_future_effective_price REAL,
    disclaimer TEXT NOT NULL
);

-- 2. Tabela de Detalhamento das Cotações de Contratos Futuros Utilizados na Análise
CREATE TABLE IF NOT EXISTS analysis_futures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT NOT NULL,
    symbol TEXT NOT NULL,                  -- Ex: CCMX26
    market_price REAL NOT NULL,
    effective_price REAL NOT NULL,
    margin_ct REAL NOT NULL,
    scenario_lower REAL NOT NULL,
    scenario_central REAL NOT NULL,
    scenario_upper REAL NOT NULL,
    FOREIGN KEY(analysis_id) REFERENCES analyses(analysis_id)
);

-- 3. Tabela de Recomendações Geradas na Análise
CREATE TABLE IF NOT EXISTS analysis_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT NOT NULL,
    type TEXT NOT NULL,                    -- SPOT_SALE ou FUTURE_HEDGE
    resource_need_month TEXT NOT NULL,     -- Ex: 2026-08
    contract_symbol TEXT,                  -- CCMX26 (se for hedge)
    contracts_count INTEGER,               -- Quantidade de contratos (se for hedge)
    quantity_bags INTEGER NOT NULL,        -- Sacas a comercializar ou proteger
    price_per_bag REAL NOT NULL,           -- Preço físico ou preço efetivo futuro
    estimated_revenue REAL NOT NULL,       -- Receita estimada total
    reason TEXT NOT NULL,                  -- Ex: COVER_RESOURCE_NEED
    FOREIGN KEY(analysis_id) REFERENCES analyses(analysis_id)
);
```

---

## 3. A Orquestração: fluxo ETL Diário (n8n)
Como você tem experiência em **Pentaho**, pense no **n8n** como a ferramenta visual que coordena a esteira de dados. Em vez de criar transformações KTR complexas, utilizaremos nós HTTP e JS simples.

O fluxo de execução automática que roda de segunda a sexta-feira às 12:00 (America/Sao_Paulo) segue os seguintes passos visuais no n8n:

1.  **Trigger (Cron Node)**: Configurado para disparar de segunda a sexta às `12:00`.
2.  **Get Producers (HTTP Request ou Postgres Node)**: Consulta a base de dados AgroCogito ou um endpoint simulado para pegar a lista de produtores ativos (ID, Estoque, Necessidades de Caixa, Produção Futura).
3.  **Get CEPEA (HTTP Request)**: Bate na API de mercado físico (ou retorna o JSON Mock) para coletar o último Indicador de Milho.
4.  **Get B3 CCM (HTTP Request)**: Bate no endpoint das cotações futuras da B3 (ou retorna o JSON Mock de contratos ativos).
5.  **Execute Engine (Execute Command / Python Node)**:
    *   O n8n formata um JSON consolidado com as três entradas e invoca o motor de recomendação Python.
    *   *Alternativa Prática*: Você pode expor o motor Python como uma mini API usando **FastAPI** ou executá-lo diretamente via linha de comando (`Execute Command` no n8n passando o JSON como argumento ou gravando um arquivo temporário no disco).
6.  **Insert Snapshot (SQL Nodes)**:
    *   O n8n lê a resposta JSON estruturada gerada pelo motor.
    *   Usando nós de banco de dados (SQLite/Postgres), ele realiza o INSERT nas tabelas `analyses`, `analysis_futures` e `analysis_recommendations` para garantir a auditabilidade permanente.
7.  **Generate PDF / Notify (HTTP Request / Email Node)**:
    *   Caso haja `OPPORTUNITY`, o n8n pode opcionalmente disparar um alerta por email/WhatsApp para o produtor ou apenas disponibilizar o link do PDF recém-gerado.

---

## 4. A Interface e o Simulador (Streamlit em Python)
Esqueça o desenvolvimento tradicional de frontend (HTML/CSS/JS). Para um MVP, a ferramenta mais prática é o **Streamlit**. Ele permite criar uma aplicação web interativa em menos de 100 linhas de código Python.

Aqui está a estrutura de como construir a tela do simulador e da análise oficial no seu arquivo `app.py`:

```python
import streamlit as st
import json
# Importamos o motor determinístico criado na Fase 1
from engine import run_recommendation_engine 

st.title("AgroCogito MVP — Serviço de Comercialização e Hedge de Milho")

# Menu Lateral / Carregamento de Dados
st.sidebar.header("Configurações do Produtor")
# No MVP Real, estes dados viriam da consulta SQL de snapshots ou da API do Produtor
producer_id = st.sidebar.selectbox("Selecionar Produtor", ["PROD-001 (Fazenda Horizonte)"])

# Seletor do modo de execução do MVP
market_mode = st.sidebar.radio("Modo de Dados de Mercado", ["MOCK", "REAL"])

# Seção de Simulação Interativa (Fase de Negociação do Produtor)
st.subheader("Simulador Interativo de Cenários")
col1, col2, col3 = st.columns(3)

with col1:
    sim_spot = st.number_input("Preço Spot Simulado (R$/saca)", value=70.00)
    sim_ct = st.number_input("Custo Total - CT (R$/saca)", value=66.80)
with col2:
    sim_future = st.number_input("Preço B3 CCMX26 Simulado (R$/saca)", value=77.30)
    sim_basis = st.number_input("Base Esperada (R$/saca)", value=-3.00)
with col3:
    sim_need = st.number_input("Necessidade Financeira Imediata (R$)", value=100000.00)

# Ao mudar qualquer valor, recalculamos instantaneamente na tela
if st.button("Executar Simulação"):
    # Criamos os dicionários temporários e rodamos o motor
    # O resultado simulado é exibido instantaneamente na tela, sem alterar o banco de dados oficial!
    st.success("Cenário recalculado com sucesso!")
    # Renderizar tabelas e novos cards dinâmicos...
```

---

## 5. Como executar o Motor Agora mesmo
Você já possui o código matemático completo salvo no diretório temporário do seu ambiente. Para validar o comportamento determinístico e analisar a estrutura de dados retornada, você pode abrir um terminal e rodar o arquivo de teste:

```bash
python3 test_engine.py
```

O script usará os dados estruturados idênticos à especificação técnica oficial e gerará as recomendações consolidadas para a **Fazenda Horizonte**, incluindo a venda spot de 1.429 sacas para Agosto e os hedges futuros via CCMX26 de 6 contratos para Outubro e 8 contratos para Dezembro.
