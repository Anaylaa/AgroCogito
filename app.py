# pyrefly: ignore [missing-import]

# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
# pyrefly: ignore [missing-import]
import altair as alt
import json
import os

from config import (
    MOCK_PRODUCER_DATA,
    MOCK_CEPEA_DATA,
    MOCK_B3_DATA,
    MARKET_DATA_MODE
)

from engine import analyze_marketing_strategy

from database import (
    save_analysis,
    get_all_analyses
)

from pdf_generator import generate_report_pdf


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="AgroCogito | Corn Marketing & Hedge",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PALETA AGROCOGITO
# ============================================================

GREEN_DARK = "#154734"
GREEN = "#48683E"
GREEN_LIGHT = "#E1E9D8"

MAIZE = "#F2C94C"
GOLD = "#D9A441"
MAIZE_LIGHT = "#FCF1BE"

CREAM = "#F8F5E8"
BACKGROUND = "#FCFBF7"

TEXT = "#29332D"
TEXT_LIGHT = "#69756D"

RED = "#A43F3F"
RED_LIGHT = "#F5E3E0"

ORANGE = "#B77422"
ORANGE_LIGHT = "#F8EBCF"

WHITE = "#FFFFFF"
BORDER = "#E2E2D8"


# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
    <style>

    /* -------------------------------------------------------
       FUNDO
    ------------------------------------------------------- */

    .stApp {{
        background-color: {BACKGROUND};
    }}

    .main {{
        background-color: {BACKGROUND};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }}


    /* -------------------------------------------------------
       SIDEBAR
    ------------------------------------------------------- */

    section[data-testid="stSidebar"] {{
        background-color: {GREEN_DARK};
    }}

    section[data-testid="stSidebar"] * {{
        color: white;
    }}

    section[data-testid="stSidebar"] .stNumberInput input {{
        background-color: rgba(255,255,255,0.95);
        color: {TEXT};
        border-radius: 8px;
        border: none;
    }}

    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.15);
    }}


    /* -------------------------------------------------------
       HEADER AGROCOGITO
    ------------------------------------------------------- */

    .agro-header {{
        background: linear-gradient(
            135deg,
            {GREEN_DARK} 0%,
            {GREEN} 100%
        );

        padding: 25px 30px;
        border-radius: 16px;
        margin-bottom: 25px;

        box-shadow: 0 8px 25px rgba(21,71,52,0.12);
    }}

    .agro-brand {{
        color: {MAIZE};
        font-size: 13px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }}

    .agro-title {{
        color: white;
        font-size: 31px;
        font-weight: 800;
        margin: 0;
        line-height: 1.15;
    }}

    .agro-subtitle {{
        color: #DDE7DC;
        font-size: 14px;
        margin-top: 8px;
    }}

    .market-badge {{
        display: inline-block;
        margin-top: 15px;
        background: rgba(242,201,76,0.15);
        border: 1px solid rgba(242,201,76,0.4);
        color: {MAIZE};
        border-radius: 20px;
        padding: 6px 12px;
        font-size: 11px;
        font-weight: 700;
    }}


    /* -------------------------------------------------------
       SECTION HEADERS
    ------------------------------------------------------- */

    .section-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 25px;
        margin-bottom: 15px;
    }}

    .section-number {{
        background-color: {MAIZE};
        color: {GREEN_DARK};
        width: 27px;
        height: 27px;
        border-radius: 8px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 12px;
        font-weight: 800;
    }}

    .section-title {{
        color: {GREEN_DARK};
        font-size: 19px;
        font-weight: 800;
    }}

    .section-line {{
        height: 2px;
        background-color: {MAIZE};
        opacity: 0.6;
        flex-grow: 1;
        margin-left: 8px;
    }}


    /* -------------------------------------------------------
       KPI CARDS
    ------------------------------------------------------- */

    .kpi-card {{
        background-color: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 14px;

        padding: 18px;

        min-height: 125px;

        box-shadow:
            0 4px 12px rgba(21,71,52,0.05);

        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }}

    .kpi-card:hover {{
        transform: translateY(-2px);

        box-shadow:
            0 8px 20px rgba(21,71,52,0.10);
    }}

    .kpi-label {{
        color: {TEXT_LIGHT};
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }}

    .kpi-value {{
        color: {GREEN_DARK};
        font-size: 25px;
        font-weight: 800;
        margin-top: 8px;
    }}

    .kpi-value.gold {{
        color: {GOLD};
    }}

    .kpi-value.positive {{
        color: {GREEN};
    }}

    .kpi-value.negative {{
        color: {RED};
    }}

    .kpi-sub {{
        color: {TEXT_LIGHT};
        font-size: 11px;
        margin-top: 6px;
    }}


    /* -------------------------------------------------------
       STATUS
    ------------------------------------------------------- */

    .status-card {{
        background-color: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 14px;

        padding: 20px 24px;

        margin-bottom: 20px;
    }}

    .status-label {{
        color: {TEXT_LIGHT};
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}

    .status-value {{
        color: {GREEN_DARK};
        font-size: 24px;
        font-weight: 800;
        margin-top: 4px;
    }}

    .status-badge {{
        display: inline-block;
        padding: 7px 15px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
    }}

    .status-opportunity {{
        background-color: {GREEN_LIGHT};
        color: {GREEN_DARK};
    }}

    .status-partial {{
        background-color: {ORANGE_LIGHT};
        color: {ORANGE};
    }}

    .status-wait {{
        background-color: {RED_LIGHT};
        color: {RED};
    }}


    /* -------------------------------------------------------
       RECOMMENDATION CARD
    ------------------------------------------------------- */

    .recommendation-card {{
        background-color: {WHITE};

        border: 1px solid {BORDER};
        border-left: 5px solid {MAIZE};

        border-radius: 12px;

        padding: 20px 22px;

        margin-bottom: 15px;

        box-shadow:
            0 4px 12px rgba(21,71,52,0.04);
    }}

    .recommendation-title {{
        color: {GREEN_DARK};
        font-size: 15px;
        font-weight: 800;
    }}

    .recommendation-subtitle {{
        color: {TEXT_LIGHT};
        font-size: 11px;
        margin-top: 2px;
    }}

    .recommendation-metric {{
        margin-top: 14px;
    }}

    .recommendation-label {{
        color: {TEXT_LIGHT};
        font-size: 9px;
        font-weight: 700;
        text-transform: uppercase;
    }}

    .recommendation-value {{
        color: {TEXT};
        font-size: 14px;
        font-weight: 700;
    }}

    .reason-box {{
        background-color: {CREAM};
        border-radius: 8px;
        padding: 10px 13px;

        color: {TEXT_LIGHT};
        font-size: 11px;

        margin-top: 14px;
    }}


    /* -------------------------------------------------------
       INFO CARD
    ------------------------------------------------------- */

    .info-card {{
        background-color: {CREAM};
        border-radius: 12px;

        padding: 18px;

        border: 1px solid #EEE9D7;
    }}


    /* -------------------------------------------------------
       BOTÕES
    ------------------------------------------------------- */

    .stButton > button {{
        border-radius: 8px;
        font-weight: 700;
        border: 1px solid {GREEN_DARK};
    }}

    .stDownloadButton > button {{
        border-radius: 8px;
        font-weight: 700;
    }}


    /* -------------------------------------------------------
       TABS
    ------------------------------------------------------- */

    button[data-baseweb="tab"] {{
        font-weight: 700;
        color: {TEXT_LIGHT};
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {GREEN_DARK};
    }}


    /* -------------------------------------------------------
       DATAFRAME
    ------------------------------------------------------- */

    [data-testid="stDataFrame"] {{
        border-radius: 10px;
        overflow: hidden;
    }}


    /* -------------------------------------------------------
       DIVISÓRIAS
    ------------------------------------------------------- */

    hr {{
        border-color: {BORDER};
        margin-top: 25px;
        margin-bottom: 25px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def money(value):
    """
    Formata valores monetários no padrão brasileiro.
    """
    return (
        f"R$ {value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def section(number, title):
    """
    Cria cabeçalho padronizado para cada seção.
    """

    st.markdown(
        f"""
        <div class="section-header">

            <div class="section-number">
                {number}
            </div>

            <div class="section-title">
                {title}
            </div>

            <div class="section-line"></div>

        </div>
        """,
        unsafe_allow_html=True
    )


def kpi_card(label, value, subtitle="", variant=""):
    """
    Cria um card de indicador.
    """

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-label">
                {label}
            </div>

            <div class="kpi-value {variant}">
                {value}
            </div>

            <div class="kpi-sub">
                {subtitle}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


def get_status_config(status):

    configs = {

        "OPPORTUNITY": {
            "label": "OPORTUNIDADE",
            "class": "status-opportunity"
        },

        "PARTIAL": {
            "label": "OPORTUNIDADE PARCIAL",
            "class": "status-partial"
        },

        "WAIT": {
            "label": "AGUARDAR",
            "class": "status-wait"
        }

    }

    return configs.get(
        status,
        {
            "label": status,
            "class": "status-partial"
        }
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
    <div class="agro-header">

        <div class="agro-brand">
            AGROCOGITO
        </div>

        <div class="agro-title">
            Comercialização & Hedge de Milho
        </div>

        <div class="agro-subtitle">
            Sistema de apoio à decisão baseado em custos,
            mercado físico e contratos futuros.
        </div>

        <div class="market-badge">
            ● MODO DE DADOS: {MARKET_DATA_MODE}
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:22px;
            font-weight:800;
            color:#F2C94C;
            margin-bottom:3px;
        ">
            🌽 AGROCOGITO
        </div>

        <div style="
            font-size:11px;
            color:#DDE7DC;
            margin-bottom:25px;
        ">
            Corn Marketing & Hedge Service
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "### Parâmetros do Produtor"
    )

    st.info(
        "Dados padrão carregados da "
        "**Fazenda Horizonte (PROD-001)**."
    )

    st.markdown("---")

    # --------------------------------------------------------
    # CUSTOS
    # --------------------------------------------------------

    st.markdown(
        "#### Custos de Referência"
    )

    coe_input = st.number_input(
        "COE — Custo Operacional Efetivo",
        value=float(
            MOCK_PRODUCER_DATA["costs"]["coePerBag"]
        ),
        step=0.50
    )

    cot_input = st.number_input(
        "COT — Custo Operacional Total",
        value=float(
            MOCK_PRODUCER_DATA["costs"]["cotPerBag"]
        ),
        step=0.50
    )

    ct_input = st.number_input(
        "CT — Custo Total",
        value=float(
            MOCK_PRODUCER_DATA["costs"]["ctPerBag"]
        ),
        step=0.50
    )

    breakeven_input = st.number_input(
        "Ponto de Equilíbrio",
        value=float(
            MOCK_PRODUCER_DATA["costs"][
                "financialBreakEvenPerBag"
            ]
        ),
        step=0.50
    )

    st.markdown("---")

    # --------------------------------------------------------
    # ESTOQUE
    # --------------------------------------------------------

    st.markdown(
        "#### Estoque & Hedge"
    )

    inventory_input = st.number_input(
        "Estoque Físico Atual (sacas)",
        value=int(
            MOCK_PRODUCER_DATA["inventory"][
                "availableBags"
            ]
        ),
        step=100
    )

    expected_basis_input = st.number_input(
        "Base Esperada (R$/saca)",
        value=float(
            MOCK_PRODUCER_DATA["hedgeParameters"][
                "expectedBasisPerBag"
            ]
        ),
        step=0.10
    )

    basis_risk_input = st.number_input(
        "Risco de Base (R$/saca)",
        value=float(
            MOCK_PRODUCER_DATA["hedgeParameters"][
                "basisRiskPerBag"
            ]
        ),
        step=0.10
    )

    op_cost_input = st.number_input(
        "Custo Operacional Hedge B3",
        value=float(
            MOCK_PRODUCER_DATA["hedgeParameters"][
                "b3OperationalCostPerBag"
            ]
        ),
        step=0.05
    )


# ============================================================
# ATUALIZAÇÃO DOS DADOS DO PRODUTOR
# ============================================================

producer_current = json.loads(
    json.dumps(MOCK_PRODUCER_DATA)
)

producer_current["costs"]["coePerBag"] = coe_input
producer_current["costs"]["cotPerBag"] = cot_input
producer_current["costs"]["ctPerBag"] = ct_input
producer_current["costs"]["financialBreakEvenPerBag"] = (
    breakeven_input
)

producer_current["inventory"]["availableBags"] = (
    inventory_input
)

producer_current["hedgeParameters"][
    "expectedBasisPerBag"
] = expected_basis_input

producer_current["hedgeParameters"][
    "basisRiskPerBag"
] = basis_risk_input

producer_current["hedgeParameters"][
    "b3OperationalCostPerBag"
] = op_cost_input


# ============================================================
# EXECUÇÃO DO MOTOR
# ============================================================

official_analysis = analyze_marketing_strategy(
    producer_current,
    MOCK_CEPEA_DATA,
    MOCK_B3_DATA,
    bypass_time_validation=True
)


# ============================================================
# TABS PRINCIPAIS
# ============================================================

tab_main, tab_sim, tab_history = st.tabs(
    [
        "📊  Análise Oficial",
        "🧪  Simulador",
        "🗄️  Auditoria"
    ]
)


# ============================================================
# ABA 1 — ANÁLISE OFICIAL
# ============================================================

with tab_main:

    # --------------------------------------------------------
    # CABEÇALHO DA ANÁLISE
    # --------------------------------------------------------

    section(
        "01",
        "Análise Oficial Diária"
    )

    st.markdown(
        f"""
        <div class="info-card">

        <b style="color:{GREEN_DARK};">
        Execução oficial de mercado
        </b>

        <br>

        <span style="font-size:12px;color:{TEXT_LIGHT};">
        A análise utiliza os preços físicos oficiais CEPEA
        e as cotações de contratos futuros B3 disponíveis
        no conjunto de dados configurado.
        </span>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    # --------------------------------------------------------
    # BOTÕES
    # --------------------------------------------------------

    col_btn1, col_btn2, col_btn3 = st.columns(
        [1.4, 1.4, 3.2]
    )

    with col_btn1:

        if st.button(
            "💾 Gravar Snapshot",
            type="primary",
            use_container_width=True
        ):

            save_analysis(
                analysis_id=official_analysis["analysisId"],
                producer_id=official_analysis["producerId"],
                producer_name=official_analysis["producerName"],
                generated_at=official_analysis["generatedAt"],
                status=official_analysis["status"],
                inputs_json_str=json.dumps(
                    {
                        "producer": producer_current,
                        "cepea": MOCK_CEPEA_DATA,
                        "b3": MOCK_B3_DATA
                    }
                ),
                recommendations=official_analysis[
                    "recommendations"
                ]
            )

            st.success(
                f"Snapshot {official_analysis['analysisId']} "
                "gravado."
            )

    with col_btn2:

        os.makedirs(
            "scratch",
            exist_ok=True
        )

        pdf_filename = (
            f"scratch/"
            f"{official_analysis['analysisId']}.pdf"
        )

        generate_report_pdf(
            official_analysis,
            pdf_filename
        )

        with open(
            pdf_filename,
            "rb"
        ) as f:

            st.download_button(
                label="📥 Baixar PDF",
                data=f,
                file_name=(
                    f"Relatorio_"
                    f"{official_analysis['analysisId']}.pdf"
                ),
                mime="application/pdf",
                use_container_width=True
            )


    # --------------------------------------------------------
    # IDENTIFICAÇÃO
    # --------------------------------------------------------

    section(
        "02",
        "Resumo da Operação"
    )

    info1, info2, info3, info4 = st.columns(4)

    with info1:

        st.markdown(
            f"""
            <div class="kpi-card">

                <div class="kpi-label">
                    PRODUTOR
                </div>

                <div class="kpi-value"
                     style="font-size:18px;">
                    {official_analysis['producerName']}
                </div>

                <div class="kpi-sub">
                    ID: {official_analysis['producerId']}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with info2:

        kpi_card(
            "COMMODITY",
            "MILHO",
            "Saca padrão de 60 kg"
        )

    with info3:

        kpi_card(
            "ID DA ANÁLISE",
            official_analysis["analysisId"],
            "Snapshot atual"
        )

    with info4:

        kpi_card(
            "GERADO EM",
            official_analysis["generatedAt"],
            "Data/hora da execução"
        )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    section(
        "03",
        "Diagnóstico do Sistema"
    )

    status = official_analysis["status"]

    status_config = get_status_config(status)

    if status == "OPPORTUNITY":

        diagnostic_message = (
            "Foram identificadas oportunidades "
            "economicamente atrativas para comercialização "
            "e/ou proteção de margem."
        )

    elif status == "PARTIAL":

        diagnostic_message = (
            "Parte das necessidades de caixa pode ser "
            "atendida com o estoque ou produção elegível, "
            "mas não integralmente."
        )

    elif status == "WAIT":

        diagnostic_message = (
            "Nenhuma oportunidade com margem econômica "
            "positiva foi identificada no cenário atual. "
            "A recomendação é aguardar."
        )

    else:

        diagnostic_message = (
            "Status indefinido ou dados parciais."
        )


    col_status1, col_status2 = st.columns(
        [3, 1]
    )

    with col_status1:

        st.markdown(
            f"""
            <div class="status-card">

                <div class="status-label">
                    STATUS ATUAL
                </div>

                <div class="status-value">
                    {status}
                </div>

                <div style="
                    margin-top:10px;
                    color:{TEXT_LIGHT};
                    font-size:12px;
                ">
                    {diagnostic_message}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col_status2:

        st.markdown(
            f"""
            <div class="status-card"
                 style="text-align:center;">

                <div class="status-label">
                    DIAGNÓSTICO
                </div>

                <div style="margin-top:18px;">

                    <span class="
                        status-badge
                        {status_config['class']}
                    ">
                        {status_config['label']}
                    </span>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # KPIs DE MERCADO
    # --------------------------------------------------------

    section(
        "04",
        "Indicadores Principais"
    )

    best_future = (
        official_analysis["bestFutureContract"]
    )

    best_fut_symbol = (
        best_future["symbol"]
        if best_future
        else "N/A"
    )

    best_fut_price = (
        best_future["effectivePrice"]
        if best_future
        else 0.0
    )

    best_margin = (
        best_future["marginOverCt"]
        if best_future
        else 0.0
    )


    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        kpi_card(
            "PREÇO SPOT CEPEA",
            money(
                official_analysis["spot"]["price"]
            ),
            f"Ref. {official_analysis['spot']['referenceDate']}"
        )

    with c2:

        kpi_card(
            "MELHOR FUTURO B3",
            best_fut_symbol,
            f"Efetivo: {money(best_fut_price)}",
            "gold"
        )

    with c3:

        kpi_card(
            "CUSTO TOTAL CT",
            money(
                official_analysis["costs"]["ctPerBag"]
            ),
            (
                "Break-even: "
                + money(
                    official_analysis["costs"][
                        "financialBreakEvenPerBag"
                    ]
                )
            )
        )

    with c4:

        kpi_card(
            "MELHOR MARGEM CT",
            f"{money(best_margin)}",
            "Por saca de 60 kg",
            "positive"
            if best_margin > 0
            else "negative"
        )

    with c5:

        kpi_card(
            "ESTOQUE ATUAL",
            f"{producer_current['inventory']['availableBags']:,.0f} sc",
            "Disponível imediato",
            "gold"
        )


    # --------------------------------------------------------
    # CUSTOS
    # --------------------------------------------------------

    section(
        "05",
        "Estrutura de Custos"
    )

    cost1, cost2, cost3, cost4 = st.columns(4)

    costs = official_analysis["costs"]

    with cost1:

        kpi_card(
            "COE",
            money(costs["coePerBag"]),
            "Custo Operacional Efetivo"
        )

    with cost2:

        kpi_card(
            "COT",
            money(costs["cotPerBag"]),
            "Custo Operacional Total"
        )

    with cost3:

        kpi_card(
            "CT",
            money(costs["ctPerBag"]),
            "Custo Total de Produção"
        )

    with cost4:

        kpi_card(
            "BREAK-EVEN",
            money(
                costs["financialBreakEvenPerBag"]
            ),
            "Ponto de equilíbrio planejado",
            "gold"
        )


    # --------------------------------------------------------
    # PLANO DE AÇÃO
    # --------------------------------------------------------

    section(
        "06",
        "Plano de Ação Recomendado"
    )

    recommendations = official_analysis[
        "recommendations"
    ]


    if not recommendations:

        st.warning(
            "Nenhuma oportunidade de comercialização "
            "identificada. A recomendação é **AGUARDAR** "
            "e monitorar as margens futuras."
        )

    else:

        # ----------------------------------------------------
        # GRÁFICO DE COBERTURA
        # ----------------------------------------------------

        req_data = []

        for rec in recommendations:

            need_amount = next(
                (
                    n["amount"]
                    for n in producer_current[
                        "resourceNeeds"
                    ]
                    if n["month"]
                    == rec["resourceNeedMonth"]
                ),
                0
            )

            revenue = (
                rec["estimatedRevenue"]
                if "estimatedRevenue" in rec
                else rec.get(
                    "estimatedProtectedRevenue",
                    0
                )
            )

            req_data.append(
                {
                    "Mês": rec["resourceNeedMonth"],
                    "Tipo": "Necessidade de Caixa",
                    "Valor (R$)": need_amount
                }
            )

            req_data.append(
                {
                    "Mês": rec["resourceNeedMonth"],
                    "Tipo": "Receita da Recomendação",
                    "Valor (R$)": revenue
                }
            )


        if req_data:

            df_req = pd.DataFrame(req_data)

            req_bars = (

                alt.Chart(df_req)

                .mark_bar(
                    cornerRadiusTopLeft=5,
                    cornerRadiusTopRight=5
                )

                .encode(

                    x=alt.X(
                        "Tipo:N",
                        title=None,
                        axis=alt.Axis(
                            labels=False,
                            ticks=False
                        )
                    ),

                    y=alt.Y(
                        "Valor (R$):Q",
                        title="Montante Financeiro (R$)"
                    ),

                    color=alt.Color(
                        "Tipo:N",
                        scale=alt.Scale(
                            domain=[
                                "Necessidade de Caixa",
                                "Receita da Recomendação"
                            ],
                            range=[
                                MAIZE,
                                GREEN_DARK
                            ]
                        ),
                        legend=alt.Legend(
                            title=None,
                            orient="top"
                        )
                    ),

                    column=alt.Column(
                        "Mês:N",
                        title="Cronograma de Fluxo de Caixa",
                        header=alt.Header(
                            labelFontSize=12,
                            titleFontSize=13,
                            labelFontWeight="bold"
                        )
                    )
                )

                .properties(
                    height=260
                )
            )

            st.altair_chart(
                req_bars,
                use_container_width=True
            )


        # ----------------------------------------------------
        # CARDS DAS RECOMENDAÇÕES
        # ----------------------------------------------------

        for idx, rec in enumerate(
            recommendations,
            1
        ):

            if rec["type"] == "SPOT_SALE":

                title = "VENDA SPOT"
                subtitle = (
                    "Comercialização no mercado físico"
                )

                quantity = (
                    f"{rec['quantityBags']:,} sacas"
                )

                price = money(
                    rec["pricePerBag"]
                )

                revenue = money(
                    rec["estimatedRevenue"]
                )

                extra = (
                    f"""
                    <div class="recommendation-metric">

                        <div class="recommendation-label">
                            RECEITA BRUTA ESTIMADA
                        </div>

                        <div class="recommendation-value">
                            {revenue}
                        </div>

                    </div>
                    """
                )

            else:

                title = "PROTEÇÃO FUTURA"
                subtitle = (
                    f"Hedge B3 — contrato {rec['contract']}"
                )

                quantity = (
                    f"{rec['quantityBags']:,} sacas"
                )

                price = money(
                    rec["effectivePricePerBag"]
                )

                revenue = money(
                    rec["estimatedProtectedRevenue"]
                )

                extra = (
                    f"""
                    <div class="recommendation-metric">

                        <div class="recommendation-label">
                            MARGEM SOBRE CT
                        </div>

                        <div class="recommendation-value"
                             style="color:{GREEN};">
                            +{money(
                                rec["marginOverCtPerBag"]
                            )}/saca
                        </div>

                    </div>
                    """
                )


            st.markdown(
                f"""
                <div class="recommendation-card">

                    <div class="recommendation-title">
                        RECOMENDAÇÃO {idx} · {title}
                    </div>

                    <div class="recommendation-subtitle">
                        {subtitle}
                    </div>

                    <div style="
                        display:grid;
                        grid-template-columns:
                        repeat(4,1fr);
                        gap:15px;
                    ">

                        <div class="
                            recommendation-metric
                        ">

                            <div class="
                                recommendation-label
                            ">
                                MÊS DE CAIXA
                            </div>

                            <div class="
                                recommendation-value
                            ">
                                {rec['resourceNeedMonth']}
                            </div>

                        </div>


                        <div class="
                            recommendation-metric
                        ">

                            <div class="
                                recommendation-label
                            ">
                                QUANTIDADE
                            </div>

                            <div class="
                                recommendation-value
                            ">
                                {quantity}
                            </div>

                        </div>


                        <div class="
                            recommendation-metric
                        ">

                            <div class="
                                recommendation-label
                            ">
                                PREÇO EFETIVO
                            </div>

                            <div class="
                                recommendation-value
                            ">
                                {price}/saca
                            </div>

                        </div>


                        <div class="
                            recommendation-metric
                        ">

                            <div class="
                                recommendation-label
                            ">
                                RECEITA PROTEGIDA
                            </div>

                            <div class="
                                recommendation-value
                            ">
                                {revenue}
                            </div>

                        </div>

                    </div>

                    {extra}

                    <div class="reason-box">

                        <b>Justificativa técnica:</b>
                        {rec['reason']}

                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    # --------------------------------------------------------
    # COMPARAÇÃO DE MERCADO
    # --------------------------------------------------------

    section(
        "07",
        "Comparação de Mercado"
    )

    st.caption(
        "As alternativas são comparadas de forma uniforme, "
        "trazendo os preços para o valor líquido recebido "
        "na fazenda."
    )


    chart_data = [
        {
            "Alternativa": "Spot (Físico)",
            "Margem CT (R$/sc)": (
                official_analysis["spot"][
                    "margins"
                ]["overCt"]
            )
        }
    ]


    for fut in official_analysis["futures"]:

        chart_data.append(
            {
                "Alternativa":
                    f"B3 {fut['symbol']}",

                "Margem CT (R$/sc)":
                    fut["margins"]["overCt"]
            }
        )


    df_chart = pd.DataFrame(
        chart_data
    )


    bars = (

        alt.Chart(df_chart)

        .mark_bar(
            cornerRadiusTopLeft=7,
            cornerRadiusTopRight=7
        )

        .encode(

            x=alt.X(
                "Alternativa:N",
                sort=None,
                title="",
                axis=alt.Axis(
                    labelAngle=0,
                    labelFontSize=11
                )
            ),

            y=alt.Y(
                "Margem CT (R$/sc):Q",
                title="Margem Econômica (R$/saca)"
            ),

            color=alt.condition(

                alt.datum[
                    "Margem CT (R$/sc)"
                ] >= 0,

                alt.value(GREEN),

                alt.value(RED)
            ),

            tooltip=[
                "Alternativa",
                "Margem CT (R$/sc)"
            ]
        )

        .properties(
            height=350
        )
    )


    text = (

        bars

        .mark_text(
            align="center",
            baseline="bottom",
            dy=-5,
            fontSize=12,
            fontWeight="bold"
        )

        .encode(
            text=alt.Text(
                "Margem CT (R$/sc):Q",
                format="+.2f"
            )
        )
    )


    st.altair_chart(
        bars + text,
        use_container_width=True
    )


    # --------------------------------------------------------
    # TABELA
    # --------------------------------------------------------

    comparativo_rows = []

    comparativo_rows.append(
        {
            "Alternativa": "Mercado Spot (CEPEA)",

            "Preço de Tela":
                money(
                    official_analysis[
                        "spot"
                    ]["price"]
                ),

            "Preço Efetivo":
                money(
                    official_analysis[
                        "spot"
                    ]["price"]
                ),

            "Margem COE":
                f"R$ "
                f"{official_analysis['spot']['margins']['overCoe']:+.2f}",

            "Margem COT":
                f"R$ "
                f"{official_analysis['spot']['margins']['overCot']:+.2f}",

            "Margem CT":
                f"R$ "
                f"{official_analysis['spot']['margins']['overCt']:+.2f}",

            "Status":
                "Disponível imediato"
        }
    )


    for fut in official_analysis["futures"]:

        is_best = (
            fut["symbol"]
            == best_fut_symbol
        )

        comparativo_rows.append(
            {
                "Alternativa":
                    f"B3 {fut['symbol']} "
                    f"({fut['expirationMonth']})",

                "Preço de Tela":
                    money(
                        fut["marketPrice"]
                    ),

                "Preço Efetivo":
                    money(
                        fut["effectivePrice"]
                    ),

                "Margem COE":
                    f"R$ "
                    f"{fut['margins']['overCoe']:+.2f}",

                "Margem COT":
                    f"R$ "
                    f"{fut['margins']['overCot']:+.2f}",

                "Margem CT":
                    f"R$ "
                    f"{fut['margins']['overCt']:+.2f}",

                "Status":
                    (
                        "★ Melhor margem futura"
                        if is_best
                        else "Elegível"
                    )
            }
        )


    df_comp = pd.DataFrame(
        comparativo_rows
    )


    st.dataframe(
        df_comp,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # MEMÓRIA DE CÁLCULO
    # --------------------------------------------------------

    section(
        "08",
        "Memória de Cálculo & Auditoria"
    )


    with st.expander(
        "Abrir memória de cálculo",
        expanded=False
    ):

        tab_math, tab_json = st.tabs(
            [
                "🧮 Fórmulas",
                "💻 JSON de Auditoria"
            ]
        )


        with tab_math:

            if best_fut_symbol != "N/A":

                basis = producer_current[
                    "hedgeParameters"
                ]["expectedBasisPerBag"]

                op_cost = producer_current[
                    "hedgeParameters"
                ]["b3OperationalCostPerBag"]

                market_price = next(
                    f["marketPrice"]
                    for f in official_analysis[
                        "futures"
                    ]
                    if f["symbol"]
                    == best_fut_symbol
                )

                ct = official_analysis[
                    "costs"
                ]["ctPerBag"]


                st.markdown(
                    f"""
                    ### 1. Formação do Preço Efetivo Futuro

                    **Contrato analisado:** `{best_fut_symbol}`

                    O preço efetivo considera a cotação
                    do contrato futuro, a base esperada e
                    os custos operacionais.

                    $$
                    Preço\\ Efetivo =
                    Cotação\\ B3 +
                    Base\\ Esperada -
                    Custo\\ Operacional
                    $$

                    **Cálculo:**

                    $$
                    R$\\ {market_price:.2f}
                    +
                    ({basis:+.2f})
                    -
                    R$\\ {op_cost:.2f}
                    =
                    \\mathbf{{R$\\ {best_fut_price:.2f}}}
                    $$


                    ### 2. Margem Econômica sobre CT

                    $$
                    Margem\\ CT =
                    Preço\\ Efetivo -
                    Custo\\ Total
                    $$

                    **Cálculo:**

                    $$
                    R$\\ {best_fut_price:.2f}
                    -
                    R$\\ {ct:.2f}
                    =
                    \\mathbf{{R$\\ {best_margin:+.2f}}}
                    $$


                    ### 3. Dimensionamento de Contratos

                    A operação utiliza contratos futuros
                    padronizados de milho da B3.

                    $$
                    Contratos\\ Necessários =
                    \\left\\lceil
                    \\frac{{Necessidade\\ Financeira}}
                    {{Preço\\ Efetivo}}
                    \\times
                    \\frac{{1}}{{450}}
                    \\right\\rceil
                    $$
                    """
                )

            else:

                st.info(
                    "Não há contratos futuros elegíveis "
                    "no momento para detalhar o cálculo "
                    "de hedge."
                )


        with tab_json:

            st.caption(
                "Dados completos retornados pelo motor "
                "de análise."
            )

            st.json(
                official_analysis
            )


# ============================================================
# ABA 2 — SIMULADOR
# ============================================================

with tab_sim:

    section(
        "01",
        "Simulador de Cenários"
    )

    st.markdown(
        f"""
        <div class="info-card">

        <b style="color:{GREEN_DARK};">
        E se o mercado mudar?
        </b>

        <br>

        <span style="font-size:12px;color:{TEXT_LIGHT};">
        Altere as variáveis abaixo para avaliar
        instantaneamente o impacto sobre o preço efetivo
        e a margem econômica.
        Nenhuma simulação altera o snapshot oficial.
        </span>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    col_sim1, col_sim2 = st.columns(
        2
    )


    with col_sim1:

        st.markdown(
            f"""
            <div style="
                color:{GREEN_DARK};
                font-size:16px;
                font-weight:800;
                margin-bottom:10px;
            ">
                Variáveis de Mercado
            </div>
            """,
            unsafe_allow_html=True
        )

        sim_spot_price = st.slider(
            "Preço Spot CEPEA (R$/saca)",
            min_value=50.0,
            max_value=100.0,
            value=70.0,
            step=0.50
        )

        sim_b3_price = st.slider(
            "Preço Futuro CCMX26 B3 (R$/saca)",
            min_value=50.0,
            max_value=100.0,
            value=77.30,
            step=0.50
        )

        sim_basis = st.slider(
            "Base Esperada (R$/saca)",
            min_value=-10.0,
            max_value=5.0,
            value=-3.0,
            step=0.25
        )

        sim_b3_cost = st.slider(
            "Custo Operacional B3 (R$/saca)",
            min_value=0.0,
            max_value=2.0,
            value=0.20,
            step=0.05
        )


    with col_sim2:

        st.markdown(
            f"""
            <div style="
                color:{GREEN_DARK};
                font-size:16px;
                font-weight:800;
                margin-bottom:10px;
            ">
                Variáveis da Fazenda
            </div>
            """,
            unsafe_allow_html=True
        )

        sim_ct = st.slider(
            "Custo Total CT (R$/saca)",
            min_value=40.0,
            max_value=90.0,
            value=66.80,
            step=0.50
        )


    # --------------------------------------------------------
    # CÁLCULOS
    # --------------------------------------------------------

    sim_effective_spot = sim_spot_price

    sim_effective_future = round(
        sim_b3_price
        + sim_basis
        - sim_b3_cost,
        2
    )

    margin_spot_sim = round(
        sim_effective_spot
        - sim_ct,
        2
    )

    margin_future_sim = round(
        sim_effective_future
        - sim_ct,
        2
    )


    official_effective_spot = (
        official_analysis[
            "spot"
        ]["price"]
    )

    official_effective_future = (
        official_analysis[
            "bestFutureContract"
        ]["effectivePrice"]
        if official_analysis[
            "bestFutureContract"
        ]
        else 0.0
    )

    official_margin_spot = (
        official_analysis[
            "spot"
        ]["margins"]["overCt"]
    )

    official_margin_future = (
        official_analysis[
            "bestFutureContract"
        ]["marginOverCt"]
        if official_analysis[
            "bestFutureContract"
        ]
        else 0.0
    )


    # --------------------------------------------------------
    # RESULTADOS
    # --------------------------------------------------------

    section(
        "02",
        "Resultado da Simulação"
    )


    s1, s2, s3, s4 = st.columns(4)


    with s1:

        kpi_card(
            "SPOT SIMULADO",
            money(sim_effective_spot),
            f"Oficial: {money(official_effective_spot)}"
        )

    with s2:

        kpi_card(
            "MARGEM SPOT",
            f"{money(margin_spot_sim)}",
            f"Oficial: {money(official_margin_spot)}",
            "positive"
            if margin_spot_sim >= 0
            else "negative"
        )

    with s3:

        kpi_card(
            "FUTURO SIMULADO",
            money(sim_effective_future),
            f"Oficial: {money(official_effective_future)}",
            "gold"
        )

    with s4:

        kpi_card(
            "MARGEM FUTURA",
            f"{money(margin_future_sim)}",
            f"Oficial: {money(official_margin_future)}",
            "positive"
            if margin_future_sim >= 0
            else "negative"
        )


    st.markdown("")

    sim_data = {

        "Métrica": [
            "Preço Efetivo Spot",
            "Margem Spot (CT)",
            "Preço Efetivo Futuro",
            "Margem Futuro (CT)"
        ],

        "Oficial": [
            money(official_effective_spot),
            f"{money(official_margin_spot)}",
            money(official_effective_future),
            f"{money(official_margin_future)}"
        ],

        "Simulado": [
            money(sim_effective_spot),
            f"{money(margin_spot_sim)}",
            money(sim_effective_future),
            f"{money(margin_future_sim)}"
        ]
    }


    st.dataframe(
        pd.DataFrame(sim_data),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# ABA 3 — HISTÓRICO
# ============================================================

with tab_history:

    section(
        "01",
        "Histórico de Auditoria"
    )

    st.markdown(
        f"""
        <div class="info-card">

        <b style="color:{GREEN_DARK};">
        Snapshots das decisões
        </b>

        <br>

        <span style="font-size:12px;color:{TEXT_LIGHT};">
        Cada análise oficial gravada representa um registro
        histórico do momento da decisão e dos dados utilizados.
        </span>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    history = get_all_analyses()


    if not history:

        st.info(
            "Nenhuma análise foi gravada ainda. "
            "Execute a análise oficial e clique em "
            "**Gravar Snapshot**."
        )

    else:

        df_hist = pd.DataFrame(
            history
        )

        st.metric(
            "Snapshots registrados",
            len(df_hist)
        )

        st.markdown("")

        st.dataframe(
            df_hist,
            use_container_width=True,
            hide_index=True
        )