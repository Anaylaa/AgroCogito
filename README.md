# Especificação Funcional do MVP — AgroCogito

## 1. Objetivo

A **AgroCogito** é uma plataforma fictícia para apoio à gestão e comercialização de commodities agrícolas.

O objetivo deste MVP é desenvolver um novo serviço capaz de combinar:

* dados econômicos e produtivos de um produtor rural;
* preço físico de referência do milho;
* cotações dos contratos futuros de milho negociados na B3;

para gerar automaticamente uma **recomendação diária de comercialização de milho**.

O sistema deverá responder principalmente:

1. Quanto milho o produtor possui disponível ou terá disponível?
2. Quanto recurso financeiro ele precisa em cada período?
3. É necessário vender milho agora para gerar caixa?
4. Qual é a margem da venda no mercado físico?
5. Quais contratos futuros da B3 estão disponíveis?
6. Qual contrato futuro apresenta a melhor margem estimada?
7. Quantas sacas devem ser vendidas no mercado físico?
8. Quantos contratos futuros devem ser utilizados para hedge?
9. É melhor realizar alguma operação ou aguardar?

O sistema é exclusivamente uma ferramenta de **apoio à decisão**.

Ele não deverá executar ordens na B3, realizar vendas, contratar hedge ou movimentar recursos financeiros.

---

# 2. Escopo do MVP

O MVP deve contemplar exclusivamente:

**Commodity**

* Milho.

**Mercado físico**

* Indicador de Milho CEPEA/ESALQ.

**Mercado derivativo**

* Contrato Futuro de Milho B3 — CCM.

**Funcionalidades**

* integração com dados de um produtor;
* obtenção do último preço CEPEA disponível;
* obtenção das cotações dos contratos futuros CCM;
* cálculo das margens;
* identificação dos contratos elegíveis;
* determinação da quantidade necessária para atender necessidades financeiras;
* cálculo da quantidade possível de hedge;
* geração de uma estratégia combinada;
* recomendação de aguardar quando não houver oportunidade;
* página web para apresentação dos resultados;
* simulador interativo;
* memória completa dos cálculos;
* geração de relatório em PDF;
* armazenamento das análises realizadas.

A análise oficial deverá ser executada **uma vez por dia útil, às 12h, horário de Brasília**.

---

# 3. Arquitetura conceitual

Embora a funcionalidade seja apresentada ao usuário como parte da AgroCogito, o motor de recomendação deverá ser implementado como um serviço separado.

```text
┌──────────────────────────┐
│      AgroCogito          │
│ Dados do produtor        │
└────────────┬─────────────┘
             │ API
             ▼
┌──────────────────────────┐
│ AgroCogito Adapter       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ Recommendation Service   │
└───────┬─────────┬────────┘
        │         │
        │         │
        ▼         ▼
     CEPEA      B3 CCM
        │         │
        └────┬────┘
             ▼
┌──────────────────────────┐
│ Recommendation Engine    │
└────────────┬─────────────┘
             │
       ┌─────┴─────┐
       ▼           ▼
   Database      PDF
       │
       ▼
┌──────────────────────────┐
│      Web Interface       │
└──────────────────────────┘
```

O motor responsável pelos cálculos deve ser **determinístico**.

Os mesmos dados de entrada devem sempre gerar os mesmos resultados.

---

# 4. Modos de execução

Para facilitar desenvolvimento e testes, a aplicação deverá possuir dois modos para obtenção dos dados externos:

```text
MARKET_DATA_MODE=MOCK
```

e

```text
MARKET_DATA_MODE=REAL
```

No modo `MOCK`, os valores definidos nesta especificação serão utilizados.

No modo `REAL`, os adapters consultarão os provedores externos configurados.

Todas as demais etapas da aplicação devem ser exatamente iguais nos dois modos.

Isso permitirá desenvolver, testar e demonstrar todo o MVP mesmo antes da contratação ou disponibilização das APIs definitivas de mercado.

---

# 5. Dados necessários da AgroCogito

O serviço deverá receber os seguintes dados para cada produtor.

## 5.1 Identificação

* identificador do produtor;
* nome do produtor;
* commodity;
* data de referência.

## 5.2 Custos

Os custos devem ser informados **por saca de 60 kg**.

### COE — Custo Operacional Efetivo

Representa os desembolsos diretamente relacionados à produção.

Exemplos:

* sementes;
* fertilizantes;
* defensivos;
* combustível;
* mão de obra;
* serviços terceirizados;
* manutenção;
* aluguel;
* demais desembolsos operacionais.

### COT — Custo Operacional Total

É formado por:

```text
COT = COE + Depreciações
```

### CT — Custo Total

É formado por:

```text
CT = COT + Custo de Oportunidade
```

Para o motor de recomendação, COE, COT e CT serão recebidos já calculados por saca.

O **CT será o principal custo utilizado para comparar economicamente as alternativas**.

## 5.3 Preço de equilíbrio financeiro

É o preço mínimo planejado por saca necessário para que a produção atinja o equilíbrio financeiro definido pelo produtor.

Esse valor será mostrado na análise, mas o principal critério de margem continuará sendo o CT.

## 5.4 Estoque atual

Quantidade de milho já produzida e atualmente disponível para comercialização.

Unidade:

```text
sacas de 60 kg
```

## 5.5 Produção futura

Para cada produção futura devem ser informados:

* mês em que o produto estará disponível;
* quantidade esperada de sacas.

## 5.6 Necessidade de recursos

O produtor poderá informar necessidades financeiras distribuídas por mês.

Exemplo:

```text
Agosto  → R$ 100.000
Outubro → R$ 180.000
Dezembro → R$ 250.000
```

Essas necessidades serão utilizadas para calcular quanto produto precisa ser convertido ou protegido para suportar o planejamento financeiro.

## 5.7 Base esperada

Para este MVP:

```text
Base = Preço físico esperado - Preço futuro
```

A base será recebida como valor em reais por saca.

Exemplo:

```text
Base esperada = -R$ 3,00/saca
```

## 5.8 Risco de base

Representa a possível variação da base utilizada para construir cenários pessimista e otimista.

Exemplo:

```text
Risco de base = R$ 1,00/saca
```

## 5.9 Custo operacional do hedge

Será recebido como custo estimado em reais por saca.

Exemplo:

```text
R$ 0,20/saca
```

Esse valor deve ser descontado do preço futuro durante a comparação econômica.

---

# 6. Entrada mockada da AgroCogito

Para desenvolvimento e testes deve estar disponível o seguinte produtor padrão.

```json
{
  "producerId": "PROD-001",
  "producerName": "Fazenda Horizonte",
  "commodity": "CORN",
  "referenceDate": "2026-08-17",

  "costs": {
    "coePerBag": 57.50,
    "cotPerBag": 62.00,
    "ctPerBag": 66.80,
    "financialBreakEvenPerBag": 65.40
  },

  "hedgeParameters": {
    "expectedBasisPerBag": -3.00,
    "basisRiskPerBag": 1.00,
    "b3OperationalCostPerBag": 0.20
  },

  "inventory": {
    "availableBags": 12000
  },

  "futureProduction": [
    {
      "availableFrom": "2026-09",
      "expectedBags": 9000
    },
    {
      "availableFrom": "2026-11",
      "expectedBags": 18000
    }
  ],

  "resourceNeeds": [
    {
      "month": "2026-08",
      "amount": 100000.00
    },
    {
      "month": "2026-10",
      "amount": 180000.00
    },
    {
      "month": "2026-12",
      "amount": 250000.00
    }
  ]
}
```

---

# 7. Dados do mercado físico

O preço físico utilizado no MVP será o **Indicador de Milho CEPEA/ESALQ**, expresso em:

```text
R$/saca de 60 kg
```

Como o indicador oficial do dia somente é publicado após o encerramento da coleta diária, a execução das 12h utilizará o **último indicador oficial disponível**, normalmente correspondente ao dia útil anterior.

A data de referência deve sempre ser apresentada ao usuário.

---

# 8. Mock do preço CEPEA

Para o cenário padrão:

```json
{
  "commodity": "CORN",
  "source": "CEPEA",
  "price": 70.00,
  "unit": "BRL_PER_60KG_BAG",
  "referenceDate": "2026-08-14",
  "retrievedAt": "2026-08-17T11:50:00-03:00"
}
```

Esse valor é fictício e deve ser utilizado exclusivamente para desenvolvimento e testes.

---

# 9. Dados do mercado futuro

O sistema deverá consultar todos os contratos futuros de milho CCM disponíveis.

Para cada contrato deverão existir pelo menos:

* código;
* mês de vencimento;
* data de vencimento;
* preço atual;
* timestamp da cotação;
* status.

Um contrato futuro CCM representa:

```text
450 sacas de milho de 60 kg
```

Portanto:

```text
Quantidade protegida =
Número de contratos × 450
```

Não existe contratação fracionada no cálculo do MVP.

---

# 10. Mock das cotações B3

```json
{
  "commodity": "CORN",
  "source": "B3",
  "contracts": [
    {
      "symbol": "CCMU26",
      "expirationMonth": "2026-09",
      "expirationDate": "2026-09-15",
      "price": 76.00,
      "unit": "BRL_PER_60KG_BAG",
      "quoteTimestamp": "2026-08-17T11:45:00-03:00",
      "status": "ACTIVE"
    },
    {
      "symbol": "CCMX26",
      "expirationMonth": "2026-11",
      "expirationDate": "2026-11-16",
      "price": 77.30,
      "unit": "BRL_PER_60KG_BAG",
      "quoteTimestamp": "2026-08-17T11:45:00-03:00",
      "status": "ACTIVE"
    },
    {
      "symbol": "CCMF27",
      "expirationMonth": "2027-01",
      "expirationDate": "2027-01-15",
      "price": 75.50,
      "unit": "BRL_PER_60KG_BAG",
      "quoteTimestamp": "2026-08-17T11:45:00-03:00",
      "status": "ACTIVE"
    }
  ]
}
```

---

# 11. Validação das cotações

A análise será realizada às:

```text
12:00
```

Para uma cotação B3 ser utilizada:

```text
12:00 - timestamp da cotação ≤ 60 minutos
```

Exemplo válido:

```text
Cotação: 11:45
Idade: 15 minutos
Resultado: válida
```

Exemplo inválido:

```text
Cotação: 10:40
Idade: 80 minutos
Resultado: inválida
```

Uma cotação inválida não pode participar da recomendação.

O CEPEA constitui exceção e utiliza o último indicador oficial disponível.

---

# 12. Contratos futuros elegíveis

Um contrato futuro somente poderá ser considerado quando:

1. estiver ativo;
2. possuir uma cotação válida;
3. existir quantidade suficiente de milho para pelo menos um contrato;
4. seu vencimento não ocorrer antes da disponibilidade do produto.

Exemplo:

Produção:

```text
Disponível em setembro/2026
```

Contratos:

```text
CCMU26 → setembro/2026 → elegível
CCMX26 → novembro/2026 → elegível
CCMF27 → janeiro/2027 → elegível
```

Para produção disponível em novembro:

```text
CCMU26 → setembro/2026 → não elegível
CCMX26 → novembro/2026 → elegível
CCMF27 → janeiro/2027 → elegível
```

Todos os contratos elegíveis devem ser calculados e apresentados.

---

# 13. Cálculo do mercado spot

Para o mercado spot:

```text
Preço Efetivo Spot = Preço CEPEA
```

No cenário mock:

```text
Preço Efetivo Spot = R$ 70,00
```

---

# 14. Margem da venda spot

Devem ser calculadas três margens.

## Margem sobre COE

```text
Margem COE =
Preço Spot - COE
```

No cenário mock:

```text
70,00 - 57,50 = 12,50
```

Resultado:

```text
+R$ 12,50/saca
```

## Margem sobre COT

```text
Margem COT =
Preço Spot - COT
```

```text
70,00 - 62,00 = 8,00
```

Resultado:

```text
+R$ 8,00/saca
```

## Margem econômica

```text
Margem CT =
Preço Spot - CT
```

```text
70,00 - 66,80 = 3,20
```

Resultado:

```text
+R$ 3,20/saca
```

A margem baseada no CT será utilizada como principal indicador econômico.

---

# 15. Preço efetivo do contrato futuro

A cotação do contrato futuro não deve ser comparada diretamente com o custo de produção.

É necessário considerar:

* base esperada;
* custo operacional do hedge.

A fórmula será:

```text
Preço Efetivo Futuro =
Preço Futuro B3
+ Base Esperada
- Custo Operacional
```

Como a base pode ser negativa, o cálculo deve preservar o sinal informado.

---

# 16. Exemplo — CCMU26

Entradas:

```text
Preço futuro = R$ 76,00
Base esperada = -R$ 3,00
Custo operacional = R$ 0,20
```

Cálculo:

```text
Preço efetivo =
76,00
+ (-3,00)
- 0,20
```

```text
Preço efetivo = R$ 72,80
```

---

# 17. Exemplo — CCMX26

```text
77,30
+ (-3,00)
- 0,20
=
R$ 74,10
```

Preço efetivo:

```text
R$ 74,10/saca
```

---

# 18. Exemplo — CCMF27

```text
75,50
+ (-3,00)
- 0,20
=
R$ 72,30
```

Preço efetivo:

```text
R$ 72,30/saca
```

---

# 19. Margens dos contratos futuros

As mesmas margens utilizadas no spot serão calculadas para cada contrato.

## CCMU26

Preço efetivo:

```text
R$ 72,80
```

Margem sobre COE:

```text
72,80 - 57,50 =
+R$ 15,30
```

Margem sobre COT:

```text
72,80 - 62,00 =
+R$ 10,80
```

Margem sobre CT:

```text
72,80 - 66,80 =
+R$ 6,00
```

## CCMX26

Preço efetivo:

```text
R$ 74,10
```

Margem CT:

```text
74,10 - 66,80 =
+R$ 7,30
```

## CCMF27

Preço efetivo:

```text
R$ 72,30
```

Margem CT:

```text
72,30 - 66,80 =
+R$ 5,50
```

Portanto, entre esses três contratos:

```text
CCMX26 possui a maior margem.
```

---

# 20. Risco de base

A recomendação deve apresentar também uma faixa de preço possível considerando o risco de base.

## Cenário inferior

```text
Preço Inferior =
Preço Futuro
+ Base Esperada
- Risco de Base
- Custo Operacional
```

## Cenário central

```text
Preço Central =
Preço Futuro
+ Base Esperada
- Custo Operacional
```

## Cenário superior

```text
Preço Superior =
Preço Futuro
+ Base Esperada
+ Risco de Base
- Custo Operacional
```

Para CCMX26:

```text
Preço futuro = 77,30
Base = -3,00
Risco = 1,00
Custo = 0,20
```

### Inferior

```text
77,30 - 3,00 - 1,00 - 0,20
=
R$ 73,10
```

### Central

```text
77,30 - 3,00 - 0,20
=
R$ 74,10
```

### Superior

```text
77,30 - 3,00 + 1,00 - 0,20
=
R$ 75,10
```

Tela:

```text
Faixa estimada:
R$ 73,10 — R$ 75,10/saca
```

Esses valores são cenários, e não preços garantidos.

---

# 21. Quantidade necessária para gerar recursos

Quando existir necessidade financeira imediata e estoque disponível, o sistema deverá calcular quantas sacas precisam ser vendidas.

A fórmula será:

```text
Sacas Necessárias =
ceil(
  Necessidade Financeira
  /
  Preço Efetivo Spot
)
```

Deve ser utilizado `ceil` porque uma fração de saca inferior não seria suficiente para atender integralmente ao valor necessário.

---

# 22. Exemplo de necessidade imediata

Necessidade:

```text
R$ 100.000
```

Preço spot:

```text
R$ 70,00
```

Cálculo:

```text
100.000 / 70 =
1.428,5714
```

Arredondamento:

```text
1.429 sacas
```

Receita estimada:

```text
1.429 × 70 =
R$ 100.030
```

Portanto:

```text
Recomendação:
vender 1.429 sacas no mercado spot.
```

---

# 23. Atualização do estoque disponível

Estoque inicial:

```text
12.000 sacas
```

Venda:

```text
1.429 sacas
```

Novo saldo:

```text
12.000 - 1.429 =
10.571 sacas
```

O motor deve controlar esse saldo durante toda a análise.

A mesma quantidade não poderá participar simultaneamente de duas recomendações.

---

# 24. Quantidade necessária para proteger uma necessidade futura

Quando existir uma necessidade futura e houver produção disponível antes dela, o sistema poderá calcular a quantidade mínima que precisaria estar protegida.

Fórmula inicial:

```text
Quantidade Alvo =
ceil(
  Necessidade Financeira
  /
  Preço Efetivo Futuro
)
```

Como o contrato CCM possui 450 sacas, a quantidade precisa ser convertida em contratos inteiros.

```text
Contratos Necessários =
ceil(
  Quantidade Alvo / 450
)
```

Essa quantidade somente será aceita quando:

```text
Contratos Necessários × 450
≤
Quantidade Disponível
```

Nunca poderá ser recomendado hedge superior à quantidade disponível.

---

# 25. Exemplo — necessidade de outubro

Necessidade:

```text
R$ 180.000
```

Produção disponível:

```text
9.000 sacas em setembro
```

Melhor contrato elegível:

```text
CCMX26
```

Preço efetivo:

```text
R$ 74,10
```

Quantidade necessária:

```text
180.000 / 74,10 =
2.429,15
```

Arredondamento:

```text
2.430 sacas
```

Contratos necessários:

```text
ceil(2.430 / 450)
=
6 contratos
```

Quantidade protegida:

```text
6 × 450 =
2.700 sacas
```

Receita de referência:

```text
2.700 × 74,10 =
R$ 200.070
```

Resultado:

```text
Necessidade:
R$ 180.000

Receita protegida estimada:
R$ 200.070

Necessidade coberta:
Sim
```

---

# 26. Exemplo — necessidade de dezembro

Necessidade:

```text
R$ 250.000
```

Produção disponível:

```text
18.000 sacas em novembro
```

CCMX26:

```text
R$ 74,10/saca
```

Quantidade necessária:

```text
250.000 / 74,10 =
3.373,82
```

```text
3.374 sacas
```

Número de contratos:

```text
ceil(3.374 / 450)
=
8 contratos
```

Quantidade protegida:

```text
3.600 sacas
```

Receita estimada:

```text
3.600 × 74,10 =
R$ 266.760
```

---

# 27. Regra para contratos inteiros

O sistema nunca poderá recomendar algo como:

```text
5,4 contratos
```

O resultado deverá sempre ser um número inteiro.

Quando o objetivo é **cobrir uma necessidade financeira**, poderá ser utilizado arredondamento para cima desde que a quantidade protegida continue inferior ou igual à produção disponível.

Quando o objetivo é simplesmente calcular a quantidade máxima possível de hedge:

```text
Contratos Máximos =
floor(
  Quantidade Disponível / 450
)
```

Exemplo:

```text
Quantidade disponível:
2.000 sacas
```

```text
floor(2.000 / 450)
=
4 contratos
```

Quantidade protegida:

```text
1.800 sacas
```

Saldo:

```text
200 sacas
```

---

# 28. Ordem de processamento das necessidades financeiras

As necessidades devem ser processadas em ordem cronológica.

Exemplo:

```text
Agosto
↓
Outubro
↓
Dezembro
```

O motor deve garantir que uma mesma quantidade disponível não seja comprometida duas vezes.

Cada recomendação deve registrar qual necessidade financeira está atendendo.

---

# 29. Estratégia combinada

O resultado final poderá conter múltiplas recomendações.

Com os dados mockados apresentados anteriormente, uma possível estratégia é:

### Recomendação 1 — necessidade imediata

```text
Venda Spot

Quantidade:
1.429 sacas

Preço:
R$ 70,00

Receita:
R$ 100.030

Objetivo:
Atender necessidade financeira de agosto.
```

### Recomendação 2 — necessidade de outubro

```text
Hedge B3

Contrato:
CCMX26

Contratos:
6

Quantidade:
2.700 sacas

Preço efetivo estimado:
R$ 74,10

Receita protegida de referência:
R$ 200.070

Objetivo:
Proteger recursos necessários para outubro.
```

### Recomendação 3 — necessidade de dezembro

```text
Hedge B3

Contrato:
CCMX26

Contratos:
8

Quantidade:
3.600 sacas

Preço efetivo estimado:
R$ 74,10

Receita protegida de referência:
R$ 266.760

Objetivo:
Proteger recursos necessários para dezembro.
```

---

# 30. Seleção do melhor contrato

Para cada quantidade de produção, todos os contratos elegíveis deverão ser analisados.

A principal regra será:

```text
Melhor contrato =
Contrato elegível com maior Margem CT
```

No cenário mock:

| Contrato | Preço futuro | Preço efetivo |    Margem CT |
| -------- | -----------: | ------------: | -----------: |
| CCMU26   |     R$ 76,00 |      R$ 72,80 |     +R$ 6,00 |
| CCMX26   |     R$ 77,30 |      R$ 74,10 | **+R$ 7,30** |
| CCMF27   |     R$ 75,50 |      R$ 72,30 |     +R$ 5,50 |

Portanto:

```text
Melhor contrato = CCMX26
```

---

# 31. Critério econômico de recomendação

A principal comparação será:

```text
Margem CT =
Preço Efetivo - CT
```

Onde:

```text
Margem CT > 0
```

indica preço superior ao custo total.

```text
Margem CT = 0
```

indica equilíbrio econômico.

```text
Margem CT < 0
```

indica preço inferior ao custo total.

COE e COT continuarão sendo mostrados para dar transparência à análise, mas não substituem o CT como principal referência da recomendação.

---

# 32. Recomendação “Aguardar”

O sistema não deve ser obrigado a recomendar uma operação.

Quando:

* não existir necessidade financeira que exija venda;
* e todas as alternativas apresentarem margem CT menor ou igual a zero;

a recomendação deverá ser:

```text
AGUARDAR
```

Exemplo:

> Nenhuma oportunidade economicamente atrativa foi identificada na análise de hoje. Os preços analisados permanecem iguais ou inferiores ao custo total de produção. A recomendação atual é aguardar e acompanhar a evolução do mercado.

---

# 33. Exemplo mock para cenário “Aguardar”

Custos:

```json
{
  "coePerBag": 57.50,
  "cotPerBag": 62.00,
  "ctPerBag": 76.00
}
```

Mercado:

```json
{
  "spot": 70.00,
  "futures": [
    {
      "symbol": "CCMU26",
      "effectivePrice": 72.80
    },
    {
      "symbol": "CCMX26",
      "effectivePrice": 74.10
    }
  ]
}
```

Margens:

```text
Spot:
70,00 - 76,00 = -6,00

CCMU26:
72,80 - 76,00 = -3,20

CCMX26:
74,10 - 76,00 = -1,90
```

Resultado esperado:

```json
{
  "status": "WAIT",
  "recommendations": []
}
```

---

# 34. Tela principal

A página inicial da análise deverá apresentar primeiro a resposta ao produtor e somente depois os detalhes técnicos.

Exemplo:

## Oportunidade identificada para milho

**Venda física**

Recomendamos vender **1.429 sacas** no mercado spot para atender à necessidade de recursos prevista para agosto.

Preço utilizado:

**R$ 70,00/saca**

Receita estimada:

**R$ 100.030**

**Proteção de preço**

Para as necessidades financeiras futuras, o **CCMX26** apresenta atualmente a maior margem entre os contratos elegíveis.

Preço efetivo estimado:

**R$ 74,10/saca**

Margem econômica:

**+R$ 7,30/saca**

---

# 35. Cards de resumo

A parte superior da página deverá apresentar pelo menos:

```text
Preço Spot
R$ 70,00
```

```text
Melhor Futuro
CCMX26
R$ 74,10 efetivo
```

```text
Custo Total
R$ 66,80
```

```text
Melhor Margem
+R$ 7,30/saca
```

```text
Estoque Atual
12.000 sacas
```

---

# 36. Comparação de mercado

Deve existir uma tabela semelhante a:

| Alternativa | Preço Mercado | Preço Efetivo | Margem COE | Margem COT |    Margem CT |
| ----------- | ------------: | ------------: | ---------: | ---------: | -----------: |
| Spot        |      R$ 70,00 |      R$ 70,00 |  +R$ 12,50 |   +R$ 8,00 |     +R$ 3,20 |
| CCMU26      |      R$ 76,00 |      R$ 72,80 |  +R$ 15,30 |  +R$ 10,80 |     +R$ 6,00 |
| CCMX26      |      R$ 77,30 |      R$ 74,10 |  +R$ 16,60 |  +R$ 12,10 | **+R$ 7,30** |
| CCMF27      |      R$ 75,50 |      R$ 72,30 |  +R$ 14,80 |  +R$ 10,30 |     +R$ 5,50 |

O melhor valor deve ser visualmente destacado.

---

# 37. Situação financeira

A interface deverá mostrar:

| Mês    | Necessidade | Estratégia      | Receita estimada | Situação |
| ------ | ----------: | --------------- | ---------------: | -------- |
| Ago/26 |  R$ 100.000 | Spot — 1.429 sc |       R$ 100.030 | Coberta  |
| Out/26 |  R$ 180.000 | 6 CCMX26        |       R$ 200.070 | Coberta  |
| Dez/26 |  R$ 250.000 | 8 CCMX26        |       R$ 266.760 | Coberta  |

---

# 38. Estoque e produção

Outra área deverá mostrar:

```text
Estoque disponível agora
12.000 sacas
```

```text
Produção prevista Setembro
9.000 sacas
```

```text
Produção prevista Novembro
18.000 sacas
```

Após aplicar as recomendações, a página deverá também mostrar as quantidades comprometidas.

---

# 39. Memória de cálculo

Toda recomendação deve possuir a ação:

**Ver memória de cálculo**

Exemplo para CCMX26:

```text
Contrato:
CCMX26

Cotação B3:
R$ 77,30

Base esperada:
-R$ 3,00

Custo operacional:
-R$ 0,20

Preço efetivo:
R$ 74,10


COE:
R$ 57,50

Margem sobre COE:
R$ 16,60


COT:
R$ 62,00

Margem sobre COT:
R$ 12,10


CT:
R$ 66,80

Margem econômica:
R$ 7,30


Risco de base:
R$ 1,00

Faixa estimada:
R$ 73,10 a R$ 75,10
```

Nenhum cálculo importante utilizado na recomendação deve existir apenas no backend sem possibilidade de consulta pelo usuário.

---

# 40. Simulador

A página deverá permitir a criação de cenários hipotéticos sem alterar a análise oficial.

O usuário poderá modificar pelo menos:

* preço spot;
* preço do contrato futuro;
* base;
* risco de base;
* custo operacional;
* COE;
* COT;
* CT;
* quantidade;
* necessidade financeira.

Exemplo:

```text
Preço CCMX26

R$ 77,30
[────────●─────────]
```

```text
Base

-R$ 3,00
[──────●───────────]
```

```text
CT

R$ 66,80
[────────●─────────]
```

Ao alterar uma variável, os resultados devem ser recalculados imediatamente.

---

# 41. Exemplo de simulação

Cenário original:

```text
CCMX26 = R$ 77,30
```

Preço efetivo:

```text
R$ 74,10
```

Margem CT:

```text
R$ 7,30
```

Usuário altera:

```text
CCMX26 = R$ 72,00
```

Novo preço efetivo:

```text
72,00 - 3,00 - 0,20 =
R$ 68,80
```

Nova margem:

```text
68,80 - 66,80 =
R$ 2,00
```

A interface deve atualizar automaticamente:

```text
Margem anterior:
+R$ 7,30

Margem simulada:
+R$ 2,00
```

---

# 42. Separação entre análise oficial e simulação

A página deve apresentar claramente:

```text
ANÁLISE OFICIAL
17/08/2026 — 12:00
```

e, quando o simulador for utilizado:

```text
CENÁRIO SIMULADO
Valores alterados pelo usuário
```

Uma simulação nunca poderá modificar ou substituir a análise oficial registrada no banco.

---

# 43. Relatório PDF

Cada análise oficial deverá possuir:

**Baixar relatório PDF**

O documento deverá conter:

1. identificação do produtor;
2. commodity;
3. data e hora da análise;
4. resumo executivo;
5. recomendação de venda spot;
6. recomendações de hedge;
7. estoque;
8. produção futura;
9. necessidades financeiras;
10. COE;
11. COT;
12. CT;
13. preço de equilíbrio;
14. CEPEA utilizado;
15. data do CEPEA;
16. contratos futuros analisados;
17. horário das cotações;
18. base;
19. risco de base;
20. custo operacional;
21. preços efetivos calculados;
22. margens;
23. quantidades;
24. número de contratos;
25. memória de cálculo;
26. aviso de apoio à decisão.

O conteúdo financeiro do PDF deve corresponder exatamente ao conteúdo da análise oficial armazenada.

---

# 44. Persistência da análise

Cada execução deve produzir um snapshot.

Exemplo:

```json
{
  "analysisId": "AN-20260817-PROD001",
  "producerId": "PROD-001",
  "generatedAt": "2026-08-17T12:00:00-03:00",
  "status": "OPPORTUNITY"
}
```

Deverão ser armazenados juntamente com a análise:

* dados recebidos da AgroCogito;
* CEPEA utilizado;
* cotações B3;
* parâmetros;
* resultados intermediários;
* recomendações;
* memória de cálculo.

Uma análise histórica não poderá ser recalculada automaticamente utilizando cotações novas.

---

# 45. Status possíveis da análise

O MVP deverá utilizar pelo menos:

```text
OPPORTUNITY
```

Há pelo menos uma recomendação economicamente atrativa.

```text
WAIT
```

Não existe necessidade obrigatória e não foi identificada alternativa com margem econômica positiva.

```text
PARTIAL
```

Parte das necessidades pode ser atendida, mas não existe quantidade suficiente para cobrir todas elas.

```text
MARKET_DATA_UNAVAILABLE
```

Os dados necessários de mercado estão indisponíveis ou inválidos.

```text
INVALID_PRODUCER_DATA
```

Os dados recebidos da AgroCogito são insuficientes ou inconsistentes.

---

# 46. Saída mockada completa

Com os dados utilizados nesta especificação, o motor deverá produzir uma estrutura semelhante a:

```json
{
  "analysisId": "AN-20260817-PROD001",
  "producerId": "PROD-001",
  "producerName": "Fazenda Horizonte",
  "commodity": "CORN",
  "generatedAt": "2026-08-17T12:00:00-03:00",

  "status": "OPPORTUNITY",

  "costs": {
    "coePerBag": 57.50,
    "cotPerBag": 62.00,
    "ctPerBag": 66.80,
    "financialBreakEvenPerBag": 65.40
  },

  "spot": {
    "source": "CEPEA",
    "referenceDate": "2026-08-14",
    "price": 70.00,

    "margins": {
      "overCoe": 12.50,
      "overCot": 8.00,
      "overCt": 3.20
    }
  },

  "futures": [
    {
      "symbol": "CCMU26",
      "marketPrice": 76.00,
      "effectivePrice": 72.80,

      "margins": {
        "overCoe": 15.30,
        "overCot": 10.80,
        "overCt": 6.00
      },

      "basisScenario": {
        "lower": 71.80,
        "central": 72.80,
        "upper": 73.80
      }
    },

    {
      "symbol": "CCMX26",
      "marketPrice": 77.30,
      "effectivePrice": 74.10,

      "margins": {
        "overCoe": 16.60,
        "overCot": 12.10,
        "overCt": 7.30
      },

      "basisScenario": {
        "lower": 73.10,
        "central": 74.10,
        "upper": 75.10
      }
    },

    {
      "symbol": "CCMF27",
      "marketPrice": 75.50,
      "effectivePrice": 72.30,

      "margins": {
        "overCoe": 14.80,
        "overCot": 10.30,
        "overCt": 5.50
      },

      "basisScenario": {
        "lower": 71.30,
        "central": 72.30,
        "upper": 73.30
      }
    }
  ],

  "bestFutureContract": {
    "symbol": "CCMX26",
    "effectivePrice": 74.10,
    "marginOverCt": 7.30
  },

  "recommendations": [
    {
      "type": "SPOT_SALE",
      "resourceNeedMonth": "2026-08",
      "quantityBags": 1429,
      "pricePerBag": 70.00,
      "estimatedRevenue": 100030.00,
      "reason": "COVER_RESOURCE_NEED"
    },

    {
      "type": "FUTURE_HEDGE",
      "resourceNeedMonth": "2026-10",
      "contract": "CCMX26",
      "contracts": 6,
      "quantityBags": 2700,
      "effectivePricePerBag": 74.10,
      "estimatedProtectedRevenue": 200070.00,
      "marginOverCtPerBag": 7.30,
      "reason": "COVER_FUTURE_RESOURCE_NEED"
    },

    {
      "type": "FUTURE_HEDGE",
      "resourceNeedMonth": "2026-12",
      "contract": "CCMX26",
      "contracts": 8,
      "quantityBags": 3600,
      "effectivePricePerBag": 74.10,
      "estimatedProtectedRevenue": 266760.00,
      "marginOverCtPerBag": 7.30,
      "reason": "COVER_FUTURE_RESOURCE_NEED"
    }
  ],

  "disclaimer": "Esta análise constitui ferramenta de apoio à decisão. Os valores podem sofrer alterações e não representam garantia de resultado."
}
```

---

# 47. Página em caso de dados indisponíveis

Se às 12h todas as cotações B3 forem anteriores às 11h:

```text
Mercado futuro indisponível
```

A interface deverá informar:

> As cotações disponíveis para o mercado futuro excedem o limite máximo de uma hora definido para esta análise. Por segurança, nenhuma recomendação baseada em contratos futuros foi emitida.

Se o CEPEA estiver disponível, a análise spot ainda poderá ser realizada.

O status geral poderá ser `PARTIAL` quando apenas uma parte da análise puder ser executada.

---

# 48. Dados inválidos

Exemplos que devem impedir ou limitar cálculos:

```text
CT inexistente
```

```text
Quantidade de estoque negativa
```

```text
Produção futura negativa
```

```text
Necessidade financeira negativa
```

```text
Data de produção inválida
```

```text
Base ausente
```

```text
Preço futuro zero ou negativo
```

Cada problema deverá gerar uma mensagem explícita.

O sistema não poderá substituir silenciosamente um dado ausente por zero.

---

# 49. Valores monetários e arredondamento

Os valores apresentados devem utilizar:

```text
2 casas decimais
```

Exemplo:

```text
R$ 74,10
```

Os cálculos internos poderão utilizar maior precisão.

O arredondamento para duas casas deve ocorrer apenas na apresentação final.

Quantidades de sacas deverão ser inteiras quando utilizadas em recomendações.

Contratos futuros sempre deverão ser inteiros.

---

# 50. Restrições assumidas pelo MVP

Para manter a primeira versão simples, os cálculos considerarão somente as variáveis explicitamente definidas nesta especificação.

Não entram no cálculo:

* frete;
* diferenças regionais de preço;
* armazenagem;
* impostos;
* corretagem individual;
* qualidade do milho;
* prêmio comercial;
* desconto comercial;
* custos financeiros adicionais;
* margem de garantia da B3;
* ajuste diário de posições;
* diferenças tributárias;
* inflação;
* taxa de juros;
* câmbio;
* previsões meteorológicas.

O desenvolvedor não deve tentar estimar ou incluir essas variáveis no MVP.

---

# 51. Integração com dados de mercado

O código não deve depender diretamente de um fornecedor específico.

Deve existir uma abstração semelhante a:

```typescript
interface MarketDataProvider {
  getCornSpotPrice(): Promise<SpotPrice>;

  getCornFutureContracts(): Promise<FutureContract[]>;
}
```

E implementações separadas:

```text
MockMarketDataProvider
```

e

```text
RealMarketDataProvider
```

O mesmo princípio deverá existir para os dados da AgroCogito:

```typescript
interface ProducerDataProvider {
  getProducerContext(
    producerId: string
  ): Promise<ProducerContext>;
}
```

---

# 52. API sugerida do novo serviço

## Executar análise

```http
POST /api/v1/analyses
```

Entrada:

```json
{
  "producerId": "PROD-001"
}
```

## Obter última análise

```http
GET /api/v1/producers/PROD-001/analyses/latest
```

## Obter análise específica

```http
GET /api/v1/analyses/AN-20260817-PROD001
```

## Obter PDF

```http
GET /api/v1/analyses/AN-20260817-PROD001/pdf
```

## Executar simulação

```http
POST /api/v1/analyses/AN-20260817-PROD001/simulations
```

Exemplo:

```json
{
  "ctPerBag": 70.00,
  "expectedBasisPerBag": -4.00,
  "futurePrices": {
    "CCMX26": 75.00
  }
}
```

A simulação deverá retornar os novos cálculos sem modificar a análise original.

---

# 53. Execução automática

O backend deverá possuir um job agendado para:

```text
Segunda a sexta-feira
12:00
America/Sao_Paulo
```

Fluxo:

```text
Iniciar job
    ↓
Buscar produtores
    ↓
Buscar dados econômicos
    ↓
Buscar CEPEA
    ↓
Buscar B3
    ↓
Validar dados
    ↓
Executar cálculos
    ↓
Gerar estratégia
    ↓
Persistir snapshot
    ↓
Gerar PDF
    ↓
Disponibilizar análise na aplicação
```

Para desenvolvimento, também deve ser possível executar esse processo manualmente.

---

# 54. Requisitos de auditabilidade

Toda recomendação deverá permitir reconstruir exatamente como o sistema chegou ao resultado.

Por isso devem ser persistidos:

```text
Input
+
Market Data
+
Formulas Parameters
+
Intermediate Results
+
Final Recommendation
```

Uma recomendação nunca pode conter apenas um texto como:

> Vender 2.700 sacas.

Ela deve permitir descobrir:

* qual preço foi utilizado;
* qual custo foi utilizado;
* qual necessidade financeira existia;
* qual fórmula foi aplicada;
* por que aquela quantidade foi calculada;
* por que aquele contrato foi selecionado.

---

# 55. Aviso obrigatório

A página e o PDF deverão apresentar:

> **Aviso:** Esta análise possui caráter exclusivamente informativo e constitui uma ferramenta de apoio à decisão. Os valores utilizados correspondem às informações disponíveis no momento da análise e podem sofrer alterações. As projeções e recomendações não representam garantia de preço, rentabilidade ou resultado. A decisão final de comercialização é de responsabilidade do produtor.

---

# 56. Critérios de aceite do MVP

O MVP estará funcionalmente completo quando for possível:

* receber o JSON mockado do produtor;
* receber o preço mockado do CEPEA;
* receber as cotações mockadas da B3;
* calcular corretamente COE, COT e CT como referências;
* calcular margem spot;
* calcular preço efetivo de cada futuro;
* calcular margem de cada contrato;
* calcular cenários de risco de base;
* identificar contratos elegíveis;
* selecionar o melhor contrato;
* calcular quantidade necessária para uma necessidade financeira;
* converter sacas em contratos inteiros;
* impedir hedge superior à quantidade disponível;
* gerar múltiplas recomendações;
* recomendar `WAIT` quando necessário;
* tratar cotações desatualizadas;
* exibir todas as informações em uma página web;
* permitir simulações;
* preservar a análise original;
* apresentar a memória de cálculo;
* gerar o PDF;
* persistir o snapshot da análise;
* reproduzir exatamente os resultados esperados dos dados mockados desta especificação.

---

# 57. Resumo do comportamento esperado

O funcionamento completo do MVP pode ser resumido por:

```text
Dados do produtor
        +
Custos
        +
Estoque
        +
Produção futura
        +
Necessidades financeiras
        +
Base
        +
Risco de base
        +
CEPEA
        +
Contratos CCM
        ↓
Validação
        ↓
Cálculo Spot
        ↓
Cálculo de todos os futuros elegíveis
        ↓
Comparação de margens
        ↓
Cálculo das quantidades
        ↓
Atendimento das necessidades financeiras
        ↓
Seleção da estratégia
        ↓
Recomendação
        ↓
Página Web
        +
Memória de cálculo
        +
Simulador
        +
PDF
```

O resultado esperado é um sistema que não apenas apresente preços de mercado, mas transforme os dados econômicos do produtor e as cotações disponíveis em uma **recomendação quantitativa, explicável, reproduzível e auditável de comercialização de milho**.
