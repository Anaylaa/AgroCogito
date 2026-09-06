# 🌽 AgroCogito

### Corn Marketing & Hedge Decision Service

> **Decision Intelligence para comercialização e proteção de margem no mercado de milho.**

O **AgroCogito** é um MVP de apoio à decisão desenvolvido para auxiliar produtores rurais na definição de estratégias de comercialização de milho e proteção de margem por meio de contratos futuros.

O sistema integra **dados de produção, custos, estoque, necessidades financeiras e condições de mercado** para avaliar diferentes alternativas comerciais e gerar recomendações **explicáveis, determinísticas e auditáveis**.

As principais estratégias consideradas são:

* 📦 **Venda no mercado físico (Spot)**
* 📈 **Proteção de preço por contratos futuros de milho na B3**
* ⏳ **Aguardar condições mais favoráveis de mercado**

O projeto foi concebido com foco em **determinismo, explicabilidade, rastreabilidade e auditabilidade**, permitindo registrar as condições utilizadas em cada análise e preservar o histórico das decisões.

---

## 🎯 Objetivo

A comercialização de commodities agrícolas envolve decisões que dependem simultaneamente de diferentes fatores, como:

* Custos de produção;
* Necessidades de fluxo de caixa;
* Estoque disponível;
* Expectativa de produção futura;
* Preço do mercado físico;
* Preços dos contratos futuros;
* Base regional;
* Custos de hedge;
* Risco de base.

O **AgroCogito** busca transformar essas informações em uma estratégia comercial estruturada.

Em vez de responder apenas:

> **"Qual é o preço do milho hoje?"**

o sistema busca responder:

> **"Considerando os custos da fazenda, as necessidades financeiras e as alternativas disponíveis no mercado, qual estratégia apresenta a melhor condição econômica para cada necessidade de caixa?"**

---

## ✨ Principais Funcionalidades

### 📊 Análise econômica

O sistema calcula e compara:

* Preço Spot;
* Preços dos contratos futuros;
* Preço efetivo futuro;
* COE, COT e CT;
* Margens de comercialização;
* Cenários de risco de base.

### 💰 Alocação financeira

As necessidades de caixa do produtor são organizadas cronologicamente e associadas às alternativas disponíveis:

* Estoque físico → **Venda Spot**
* Produção futura → **Hedge B3**
* Ausência de recursos elegíveis → **Aguardar**

### 📈 Estratégias de hedge

O motor considera contratos futuros de milho negociados na **B3**, avaliando:

* Quantidade de sacas a proteger;
* Número de contratos necessários;
* Preço efetivo;
* Margem CT;
* Cenários de base.

### 🗄️ Auditoria e rastreabilidade

Cada análise pode ser armazenada como um **snapshot**, permitindo reconstruir posteriormente as condições utilizadas para gerar determinada recomendação.

### 🧪 Simulação

A interface permite explorar cenários personalizados alterando variáveis como:

* Preço Spot;
* Preço B3;
* Base;
* Custo Total.

---

# 🏗️ Arquitetura

A arquitetura do AgroCogito é composta por quatro camadas principais:

```text
                         🌽 AGROCOGITO
                              │
              ┌───────────────┴───────────────┐
              │                               │
      DADOS DO PRODUTOR                DADOS DE MERCADO
              │                         CEPEA + B3
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   PYTHON ENGINE   │
                    │                   │
                    │ • Preço efetivo   │
                    │ • Margens         │
                    │ • Hedge           │
                    │ • Alocação        │
                    │ • Risco de base   │
                    └─────────┬─────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        VENDA SPOT         HEDGE B3         AGUARDAR
             │                │                │
             └────────────────┼────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
                SQLite              Streamlit
                Auditoria            Interface
                    │                   │
                    ▼                   ▼
                Snapshots           Simulador
                Históricos          Relatórios
```

---

# 🔄 Fluxo de Dados

O fluxo de dados do AgroCogito segue a seguinte estrutura:

```text
┌─────────────────────┐
│   Dados do Produtor │
│                     │
│ • Custos            │
│ • Estoque           │
│ • Produção futura   │
│ • Necessidades      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      n8n / ETL      │
│                     │
│ • Orquestração      │
│ • Validação         │
│ • Integração        │
└──────────┬──────────┘
           │
      ┌────┴─────┐
      │          │
      ▼          ▼
    CEPEA        B3
      │          │
      └────┬─────┘
           │
           ▼
┌─────────────────────┐
│    Python Engine    │
│                     │
│ • Margens           │
│ • Preço efetivo     │
│ • Hedge             │
│ • Alocação          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Recomendações    │
└──────────┬──────────┘
           │
      ┌────┴─────┐
      │          │
      ▼          ▼
   SQLite     Streamlit
      │          │
      ▼          ├── Análise
   Auditoria    ├── Simulador
                ├── Histórico
                └── PDF
```

---

# 🧩 Tecnologias

| Tecnologia        | Função                                |
| ----------------- | ------------------------------------- |
| 🐍 **Python 3**   | Motor matemático e regras de decisão  |
| 🐼 **Pandas**     | Manipulação e organização dos dados   |
| 📊 **Altair**     | Visualização de indicadores e margens |
| 🖥️ **Streamlit** | Interface web e simulador             |
| 🗄️ **SQLite**    | Persistência e auditoria              |
| 🔄 **n8n**        | Orquestração e ETL                    |
| 🧮 **SQL**        | Persistência estruturada              |
| 📄 **fpdf2**      | Geração de relatórios em PDF          |
| 🔀 **Git/GitHub** | Versionamento e colaboração           |

---

# 🧠 Motor de Recomendação

O núcleo do AgroCogito é um **motor determinístico desenvolvido em Python**.

A lógica de recomendação é centralizada para garantir que:

```text
MESMOS INPUTS
      ↓
MESMAS REGRAS
      ↓
MESMOS OUTPUTS
```

Essa característica permite obter:

* **Reprodutibilidade**
* **Testabilidade**
* **Explicabilidade**
* **Rastreabilidade**
* **Auditabilidade**

O motor recebe os dados do produtor e as informações de mercado e retorna uma estrutura organizada contendo os resultados da análise e as recomendações geradas.

---

# 📐 Modelo de Decisão

## 1. 💵 Preço Efetivo Futuro

A cotação de tela da B3 não deve ser comparada diretamente aos custos da fazenda.

Para uma comparação econômica mais adequada, o AgroCogito considera:

* Preço do contrato futuro;
* Base esperada;
* Custo operacional do hedge.

A fórmula utilizada é:

$$
Preço\ Efetivo =
Preço\ B3 + Base\ Esperada - Custo\ Operacional
$$

### Exemplo

Considerando:

| Variável       |    Valor |
| -------------- | -------: |
| Preço B3       | R$ 77,30 |
| Base esperada  | R$ -3,00 |
| Custo do hedge |  R$ 0,20 |

Temos:

$$
Preço\ Efetivo = 77,30 - 3,00 - 0,20
$$

$$
\boxed{Preço\ Efetivo = R\$ 74,10}
$$

Assim, o valor utilizado na comparação econômica é o **preço efetivo**, e não apenas a cotação observada na B3.

---

# 📊 2. Margens de Comercialização

O sistema trabalha com três níveis de custo:

### COE — Custo Operacional Efetivo

Representa os desembolsos operacionais diretos da produção.

### COT — Custo Operacional Total

Considera o COE acrescido dos custos operacionais adicionais, incluindo depreciações.

### CT — Custo Total

Considera o COT acrescido dos custos de oportunidade.

As margens são calculadas por:

$$
Margem_{COE} = Preço\ Efetivo - COE
$$

$$
Margem_{COT} = Preço\ Efetivo - COT
$$

$$
Margem_{CT} = Preço\ Efetivo - CT
$$

A **Margem CT** é utilizada como principal referência econômica para a tomada de decisão comercial.

---

# ⚠️ 3. Cenários de Risco de Base

O AgroCogito considera diferentes cenários para avaliar o impacto da variação da base esperada.

### Cenário Inferior

$$
Preço\ Futuro + Base\ Esperada - Risco\ de\ Base - Custo\ Operacional
$$

### Cenário Central

$$
Preço\ Futuro + Base\ Esperada - Custo\ Operacional
$$

### Cenário Superior

$$
Preço\ Futuro + Base\ Esperada + Risco\ de\ Base - Custo\ Operacional
$$

Essa abordagem permite avaliar como diferentes condições de base podem afetar o **preço efetivo** e a **margem econômica**.

---

# 💰 4. Alocação das Necessidades de Caixa

As necessidades financeiras do produtor são organizadas cronologicamente.

Para cada necessidade, o motor verifica os recursos disponíveis e busca uma estratégia adequada:

```text
              Necessidade Financeira
                       │
                       ▼
              Existe estoque disponível?
                    │       │
                   SIM     NÃO
                    │       │
                    ▼       ▼
               Venda Spot  Produção futura?
                               │
                          ┌────┴────┐
                         SIM       NÃO
                          │         │
                          ▼         ▼
                       Hedge B3  Aguardar
```

---

# 🌽 5. Venda Spot

Quando uma necessidade financeira pode ser atendida utilizando o estoque físico disponível, o sistema calcula a quantidade de sacas necessária:

$$
Sacas_{Spot} =
\left\lceil
\frac{Necessidade\ Financeira}
{Preço\ Spot}
\right\rceil
$$

O arredondamento para cima garante que a quantidade comercializada seja suficiente para cobrir a necessidade financeira.

---

# 📈 6. Hedge com Contratos Futuros

Quando existe produção futura elegível, o sistema pode utilizar contratos futuros de milho da B3.

Para o MVP:

> **1 contrato = 450 sacas**

A quantidade de contratos é calculada por:

$$
Contratos_{B3} =
\left\lceil
\frac{Quantidade\ Alvo\ de\ Sacas}
{450}
\right\rceil
$$

O sistema também considera a restrição de produção futura disponível, evitando que o volume protegido ultrapasse a quantidade física elegível.

---

# 🗓️ 7. Alocação Cronológica

As necessidades de caixa são processadas de acordo com sua ordem temporal.

Por exemplo:

```text
AGOSTO
   │
   └── Necessidade financeira
            │
            └── Estoque disponível
                     │
                     ▼
                 VENDA SPOT


OUTUBRO
   │
   └── Necessidade financeira
            │
            └── Produção futura
                     │
                     ▼
                  HEDGE B3


DEZEMBRO
   │
   └── Necessidade financeira
            │
            └── Produção futura
                     │
                     ▼
                  HEDGE B3
```

Dessa forma, a estratégia comercial é diretamente relacionada ao **cronograma financeiro do produtor**.

---

# 🗄️ Persistência e Auditabilidade

O MVP utiliza **SQLite** para registrar as análises oficiais.

A principal premissa é:

> **Uma decisão tomada em determinado momento deve poder ser reconstruída posteriormente.**

Por isso, cada snapshot pode armazenar:

```text
ID da análise
      +
Produtor
      +
Data/hora
      +
Custos
      +
Preço Spot
      +
Contratos futuros
      +
Preços efetivos
      +
Cenários de base
      +
Recomendações
      +
Justificativas
```

Isso evita depender exclusivamente dos preços atuais para explicar uma decisão tomada anteriormente.

---

# 🧱 Estrutura do Banco de Dados

O modelo lógico separa:

* Análise consolidada;
* Contratos futuros considerados;
* Recomendações geradas.

## `analyses`

Tabela principal responsável pelo snapshot da análise.

```sql
CREATE TABLE IF NOT EXISTS analyses (
    analysis_id TEXT PRIMARY KEY,
    producer_id TEXT NOT NULL,
    producer_name TEXT NOT NULL,
    commodity TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    status TEXT NOT NULL,
    coe_per_bag REAL NOT NULL,
    cot_per_bag REAL NOT NULL,
    ct_per_bag REAL NOT NULL,
    break_even_per_bag REAL NOT NULL,
    spot_price REAL,
    spot_ref_date TEXT,
    best_future_symbol TEXT,
    best_future_effective_price REAL,
    disclaimer TEXT NOT NULL
);
```

## `analysis_futures`

Tabela responsável pelo detalhamento dos contratos futuros considerados na análise.

```sql
CREATE TABLE IF NOT EXISTS analysis_futures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    market_price REAL NOT NULL,
    effective_price REAL NOT NULL,
    margin_ct REAL NOT NULL,
    scenario_lower REAL NOT NULL,
    scenario_central REAL NOT NULL,
    scenario_upper REAL NOT NULL,
    FOREIGN KEY (analysis_id)
        REFERENCES analyses(analysis_id)
);
```

## `analysis_recommendations`

Tabela responsável pelo armazenamento das recomendações geradas pelo motor.

```sql
CREATE TABLE IF NOT EXISTS analysis_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT NOT NULL,
    type TEXT NOT NULL,
    resource_need_month TEXT NOT NULL,
    contract_symbol TEXT,
    contracts_count INTEGER,
    quantity_bags INTEGER NOT NULL,
    price_per_bag REAL NOT NULL,
    estimated_revenue REAL NOT NULL,
    reason TEXT NOT NULL,
    FOREIGN KEY (analysis_id)
        REFERENCES analyses(analysis_id)
);
```

---

# 🔄 ETL e Orquestração com n8n

O **n8n** atua como camada de orquestração do fluxo de dados.

A arquitetura planejada é:

```text
                 ┌────────────────┐
                 │  Cron Trigger  │
                 └───────┬────────┘
                         │
                  Segunda a sexta
                       12:00
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     Produtores        CEPEA            B3
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                  Dados consolidados
                         │
                         ▼
                   Python Engine
                         │
                         ▼
                     JSON Result
                         │
                  ┌──────┴──────┐
                  ▼             ▼
               SQLite          PDF
                  │
                  ▼
               Auditoria
```

---

# ⏰ Fluxo Diário

A execução planejada ocorre de **segunda a sexta-feira, às 12:00**, considerando o timezone:

```text
America/Sao_Paulo
```

### 1. Trigger

O **Cron Node** inicia o processo.

### 2. Get Producers

Consulta os produtores ativos e seus dados:

* Identificação;
* Estoque;
* Produção futura;
* Necessidades de caixa;
* Custos.

### 3. Get CEPEA

Obtém o preço do mercado físico ou utiliza os dados MOCK durante o desenvolvimento.

### 4. Get B3

Obtém os contratos futuros de milho ativos ou utiliza os dados MOCK.

### 5. Validação

Os dados recebidos são validados antes de serem enviados ao motor.

Uma das regras previstas é a validação da atualidade da cotação B3.

### 6. Execute Engine

Os dados são consolidados em JSON e enviados ao motor Python.

### 7. Insert Snapshot

O resultado da análise é persistido no banco de dados.

### 8. Generate PDF / Notification

Caso exista uma oportunidade, o fluxo pode posteriormente ser configurado para gerar um relatório e/ou enviar uma notificação.

---

# 🧪 Dados MOCK e Dados Reais

Durante o desenvolvimento do MVP, o sistema utiliza dados estruturados de teste.

A arquitetura contempla dois modos:

```text
MOCK
  │
  └── Desenvolvimento e testes

REAL
  │
  └── Integrações com fontes externas
```

O modo **MOCK** permite desenvolver e testar o sistema sem depender de integrações externas.

Entre as estruturas utilizadas estão:

```text
MOCK_PRODUCER_DATA
MOCK_CEPEA_DATA
MOCK_B3_DATA
```

A separação entre **dados** e **motor de decisão** permite substituir posteriormente os dados MOCK por fontes reais sem alterar a lógica central de recomendação.

---

# 🖥️ Interface Streamlit

O **Streamlit** funciona como camada visual do AgroCogito.

A interface está organizada em três áreas principais:

### 📊 Análise Oficial

Apresenta:

* Status da análise;
* KPIs;
* Custos;
* Recomendações;
* Comparação de mercado;
* Memória de cálculo.

### 🧪 Simulador

Permite explorar cenários personalizados utilizando:

* Preço Spot;
* Preço B3;
* Base;
* Custo CT.

### 🗂️ Histórico

Permite consultar análises anteriores e acessar os registros produzidos pelo sistema.

---

# 📊 Visão da Interface

```text
┌─────────────────────────────────────────┐
│              🌽 AGROCOGITO              │
│        Corn Marketing & Hedge           │
├─────────────────────────────────────────┤
│                                         │
│  📊 ANÁLISE OFICIAL                     │
│                                         │
│  • Status                                │
│  • KPIs                                  │
│  • Custos                                │
│  • Recomendações                         │
│  • Comparação de mercado                 │
│  • Memória de cálculo                    │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  🧪 SIMULADOR                            │
│                                         │
│  • Cenários personalizados               │
│  • Preço Spot                            │
│  • Preço B3                              │
│  • Base                                  │
│  • Custo CT                              │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  🗂️ HISTÓRICO                            │
│                                         │
│  • Análises anteriores                   │
│  • Snapshots                             │
│  • Recomendações                         │
│                                         │
└─────────────────────────────────────────┘
```

---

# 🔐 Princípios do Projeto

O desenvolvimento do AgroCogito é orientado por cinco princípios:

| Princípio              | Aplicação                                                         |
| ---------------------- | ----------------------------------------------------------------- |
| 🎯 **Determinismo**    | Mesmas entradas produzem as mesmas decisões                       |
| 🔎 **Explicabilidade** | Cada recomendação possui justificativa                            |
| 🧭 **Rastreabilidade** | Os dados utilizados podem ser identificados                       |
| 🗄️ **Auditabilidade** | Análises podem ser reconstruídas posteriormente                   |
| 🧪 **Testabilidade**   | A lógica central pode ser validada independentemente da interface |

---

# 🚀 Fluxo de Decisão — Resumo

De forma simplificada, o processo do AgroCogito é:

```text
Dados do produtor
       │
       ▼
Dados de mercado
       │
       ▼
Validação
       │
       ▼
Cálculo do preço efetivo
       │
       ▼
Cálculo das margens
       │
       ▼
Análise dos cenários de base
       │
       ▼
Identificação das necessidades financeiras
       │
       ▼
Alocação dos recursos
       │
       ├───────────────┐
       ▼               ▼
   Estoque         Produção futura
       │               │
       ▼               ▼
   Venda Spot       Hedge B3
       │               │
       └───────┬───────┘
               ▼
         Recomendação
               │
       ┌───────┴────────┐
       ▼                ▼
    SQLite          Streamlit
       │                │
       ▼                ▼
   Auditoria       Visualização
```

---

# ⚠️ Disclaimer

O **AgroCogito é um MVP experimental de apoio à decisão**.

As recomendações produzidas pelo sistema são baseadas nas premissas, dados e regras implementadas no modelo e **não constituem recomendação financeira, comercial ou de investimento**.

As decisões efetivas de comercialização e hedge devem considerar as condições reais do mercado, os contratos disponíveis, custos envolvidos, perfil de risco e orientação de profissionais especializados.

---

# 🌽 AgroCogito

**Decision Intelligence para transformar dados agrícolas e financeiros em decisões comerciais mais estruturadas, explicáveis e rastreáveis.**
