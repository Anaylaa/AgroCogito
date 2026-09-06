# AgroCogito MVP — Corn Marketing & Hedge Decision Service

Este é o MVP do serviço de apoio à gestão e comercialização de commodities agrícolas (foco em milho) da plataforma **AgroCogito**. 

O sistema foi estruturado para ser robusto, explicável, determinístico e auditável. Ele consome dados cadastrais, produtivos e necessidades de fluxo de caixa de um produtor rural e cruza de forma inteligente com cotações físicas (CEPEA) e futuras (B3 - CCM) para recomendar a melhor estratégia de comercialização de milho.

---

## 🏗️ Arquitetura e Fluxo do Projeto

O MVP está dividido em quatro blocos que se alinham perfeitamente às tecnologias que você já domina:

1. **Ingestão e Orquestração (n8n / ETL):** Um fluxo agendado (cron) que roda todos os dias úteis às 12:00, busca dados cadastrais do produtor e preços de mercado (CEPEA e B3), realiza validação de atraso da cotação B3 (< 60 min) e envia esses insumos para o serviço em Python.
2. **Motor de Recomendação & Alocação (Python 3):** O cérebro matemático determinístico que calcula preços efetivos líquidos, margens de lucro (COE/COT/CT) e aloca as necessidades mensais de caixa do produtor de forma cronológica, consumindo estoque disponível e protegendo produções futuras usando contratos futuros cheios (450 sacas).
3. **Persistência & Auditabilidade (SQL / SQLite):** Gravação imutável de cada Snapshot e recomendação gerada em tabelas relacionais do SQLite. Garante total rastreabilidade sem reprocessamentos dinâmicos de dados passados.
4. **Interface Visual e Simulador (Streamlit):** Interface interativa rica em Python que apresenta os cards de resumo, tabela comparativa de mercado, fluxo cronológico do produtor e permite simular livremente outros cenários sem poluir as análises oficiais gravadas no banco de dados.

---

## 📂 Estrutura de Diretórios para o GitHub

Esta é a estrutura modular recomendada para subir o repositório para o seu **GitHub**:

```text
├── .gitignore               # Arquivos a serem desconsiderados pelo Git
├── README.md                # Este documento explicativo
├── requirements.txt         # Dependências do Python
├── config.py                # Parametrização do sistema (modos MOCK/REAL e dados padrões)
├── database.py              # Camada de persistência relacional usando SQLite
├── engine.py                # Motor de recomendação determinístico e lógica de alocação
├── pdf_generator.py         # Módulo para geração do relatório PDF de auditoria (via fpdf2)
├── app.py                   # Interface interativa e simulador web via Streamlit
├── test_engine.py           # Script rápido de teste de integração
└── n8n_workflow.json        # Arquivo JSON do fluxo de integração do n8n para importar
```

---

## 🧪 Lógica Matemática e Regras de Negócio

### 1. Preço Efetivo do Futuro
A cotação de tela da B3 não deve ser comparada diretamente aos custos da fazenda. Calculamos o preço líquido final recebido na fazenda aplicando a **Base Esperada** (diferença regional) e descontando o **Custo Operacional de Hedge** cobrado pela corretora/B3:
$$Preço\\ Efetivo = Preço\\ B3 + Base\\ Esperada - Custo\\ Operacional$$

### 2. Margens de Lucro por Saca
Utilizamos três métricas de custos (recebidas já calculadas por saca):
* **COE (Custo Operacional Efetivo):** Desembolsos de caixa diretos.
* **COT (Custo Operacional Total):** COE + Depreciações de maquinários.
* **CT (Custo Total):** COT + Custo de Oportunidade.
As margens são calculadas subtraindo os custos do Preço Efetivo (Spot ou Futuro). A **Margem CT** é a principal referência econômica para tomada de decisão comercial.

### 3. Alocação Cronológica e de Caixa
O motor percorre as necessidades financeiras de caixa ordenadas por mês e as soluciona sequencialmente:
* **Necessidades Imediatas (Spot):** Se houver estoque físico disponível, calcula-se as sacas necessárias arredondando para cima (`ceil`):
  $$Sacas\\ Spot = \\lceil \\frac{Necessidade\\ Financeira}{Preço\\ Spot} \\rceil$$
* **Necessidades Futuras (Hedge B3):** Se houver produção futura elegível (disponível antes do mês da necessidade de caixa), o sistema calcula a quantidade e converte em contratos cheios inteiros da B3 (450 sacas por contrato) arredondando para cima (`ceil`):
  $$Contratos\\ B3 = \\lceil \\frac{Necessidade\\ Financeira}{Preço\\ Efetivo\\ Futuro} \\times \\frac{1}{450} \\rceil$$
  *Nota:* O volume total de hedge protegido nunca poderá ultrapassar a estimativa de produção física futura do produtor para evitar over-hedging.

---

## 🚀 Como Executar o Projeto Localmente

### 1. Clonar ou Baixar os Arquivos
Baixe o código e organize-o em uma pasta no seu computador.

### 2. Criar um Ambiente Virtual (Recomendado)
No terminal da pasta do projeto, execute:
```bash
# Criar o ambiente virtual
python3 -m venv .venv

# Ativar o ambiente virtual (Linux/macOS)
source .venv/bin/activate

# Ativar o ambiente virtual (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar as Dependências
Instale os pacotes listados em `requirements.txt`:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Rodar o Teste de Integração
Você pode rodar o teste de linha de comando para validar a precisão matemática instantaneamente:
```bash
python test_engine.py
```
Isso criará automaticamente o banco de dados `agrocogito_audit.db` e executará o teste com os dados oficiais mockados da Fazenda Horizonte.

### 5. Executar o Streamlit Web App
Inicie o painel web interativo digitando:
```bash
streamlit run app.py
```
A aplicação abrirá automaticamente no seu navegador padrão no endereço `http://localhost:8501`.

---

## 🛠️ Como Integrar com o n8n

1. Abra o seu painel do **n8n**.
2. Clique no menu superior direito (três pontinhos ou menu de engrenagem) e selecione **"Import from File"** (Importar do Arquivo).
3. Selecione o arquivo `n8n_workflow.json` contido no repositório.
4. O n8n carregará toda a estrutura visual de ingestão das 12h:
   - Disparador Cron útil diário.
   - Requisições paralelas para API do Produtor, API do CEPEA e API da B3.
   - Código JS de validação de atraso de cotação (< 60 min).
   - POST final unificado para a API de decisão do AgroCogito.

---

## 📤 Como Subir para o GitHub

Na pasta do seu projeto local, execute a seguinte sequência de comandos Git no terminal:

```bash
# 1. Inicializar o repositório Git local
git init

# 2. Adicionar todos os arquivos do MVP (respeitando o .gitignore)
git add .

# 3. Criar o primeiro commit com a versão funcional
git commit -m "feat: AgroCogito MVP completo com interface Streamlit, Motor Determinístico e Integração n8n"

# 4. Criar um repositório vazio no GitHub e vincular a URL remota
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git

# 5. Enviar os códigos para a nuvem
git push -u origin main
```

---

## ⚠️ Aviso Legal Obrigatório (Apoio à Decisão)
*Aviso: Esta análise possui caráter exclusivamente informativo e constitui uma ferramenta de apoio à decisão. Os valores utilizados correspondem às informações disponíveis no momento da análise e podem sofrer alterações. As projeções e recomendações não representam garantia de preço, rentabilidade ou resultado. A decisão final de comercialização é de responsabilidade do produtor.*
