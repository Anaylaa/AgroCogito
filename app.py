import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Importar componentes internos do MVP
from config import MOCK_PRODUCER_DATA, MOCK_CEPEA_DATA, MOCK_B3_DATA, MARKET_DATA_MODE
from engine import analyze_marketing_strategy
from database import save_analysis, get_latest_analysis_for_producer, get_all_analyses
from pdf_generator import generate_report_pdf

# Configuração de Página do Streamlit
st.set_page_config(
    page_title="AgroCogito MVP — Corn Marketing",
    page_icon="🌽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado para melhorar o visual
st.markdown("""
    <style>
    .main {
        background-color: #f7f9fc;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eef2f6;
        text-align: center;
    }
    .metric-title {
        font-size: 14px;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 24px;
        color: #1e293b;
        font-weight: 700;
    }
    .metric-sub {
        font-size: 12px;
        color: #10b981;
        font-weight: 600;
        margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Título Principal do App
st.title("🌽 AgroCogito MVP: Apoio à Decisão de Comercialização e Hedge")
st.caption(f"Painel integrado em modo de dados: **{MARKET_DATA_MODE}** (Conforme especificação técnica)")

# ================= PAGE SIDEBAR / CONFIGURAÇÕES =================
with st.sidebar:
    st.header("Parâmetros do Produtor")
    st.info("Carregando dados padrão da **Fazenda Horizonte (PROD-001)**.")
    
    # Exibir informações de custos padrões
    st.subheader("Custos de Referência (R$/saca)")
    coe_input = st.number_input("COE (Custo Operacional Efetivo)", value=float(MOCK_PRODUCER_DATA["costs"]["coePerBag"]), step=0.50)
    cot_input = st.number_input("COT (Custo Operacional Total)", value=float(MOCK_PRODUCER_DATA["costs"]["cotPerBag"]), step=0.50)
    ct_input = st.number_input("CT (Custo Total de Produção)", value=float(MOCK_PRODUCER_DATA["costs"]["ctPerBag"]), step=0.50)
    breakeven_input = st.number_input("Ponto de Equilíbrio Planejado", value=float(MOCK_PRODUCER_DATA["costs"]["financialBreakEvenPerBag"]), step=0.50)
    
    st.subheader("Estoque e Proteção")
    inventory_input = st.number_input("Estoque Físico Atual (Sacas)", value=int(MOCK_PRODUCER_DATA["inventory"]["availableBags"]), step=100)
    expected_basis_input = st.number_input("Base Esperada (R$/saca)", value=float(MOCK_PRODUCER_DATA["hedgeParameters"]["expectedBasisPerBag"]), step=0.10)
    basis_risk_input = st.number_input("Risco de Base (R$/saca)", value=float(MOCK_PRODUCER_DATA["hedgeParameters"]["basisRiskPerBag"]), step=0.10)
    op_cost_input = st.number_input("Custo Operacional do Hedge B3", value=float(MOCK_PRODUCER_DATA["hedgeParameters"]["b3OperationalCostPerBag"]), step=0.05)

# Atualizar o dict do produtor de acordo com as alterações do usuário no sidebar (para a análise oficial e simulação)
producer_current = copy_prod = json.loads(json.dumps(MOCK_PRODUCER_DATA))
producer_current["costs"]["coePerBag"] = coe_input
producer_current["costs"]["cotPerBag"] = cot_input
producer_current["costs"]["ctPerBag"] = ct_input
producer_current["costs"]["financialBreakEvenPerBag"] = breakeven_input
producer_current["inventory"]["availableBags"] = inventory_input
producer_current["hedgeParameters"]["expectedBasisPerBag"] = expected_basis_input
producer_current["hedgeParameters"]["basisRiskPerBag"] = basis_risk_input
producer_current["hedgeParameters"]["b3OperationalCostPerBag"] = op_cost_input

# ================= SEÇÃO CENTRAL / ABAS DE OPERAÇÃO =================
tab_main, tab_sim, tab_history = st.tabs([
    "📈 Análise Oficial & Recomendações", 
    "🧪 Simulador Interativo de Cenários", 
    "🗄️ Histórico de Auditoria (Snapshots)"
])

# Execução automática do motor matemático para montar os dados na tela
official_analysis = analyze_marketing_strategy(
    producer_current, 
    MOCK_CEPEA_DATA, 
    MOCK_B3_DATA, 
    bypass_time_validation=True # Ignora diferença horária do mock de 2026 para permitir visualização contínua
)

# ----------------- ABA 1: ANÁLISE OFICIAL & RECOMENDAÇÕES -----------------
with tab_main:
    st.subheader("Execução Oficial Diária (12:00)")
    st.write(f"Análise baseada nos preços físicos oficiais (CEPEA) e cotações da B3 em tempo real (tolerância de 60 minutos).")
    
    # Botão para Executar a Análise e Salvar no Banco relacional de Auditoria
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("💾 Executar e Gravar Snapshot", type="primary"):
            save_analysis(
                analysis_id=official_analysis["analysisId"],
                producer_id=official_analysis["producerId"],
                producer_name=official_analysis["producerName"],
                generated_at=official_analysis["generatedAt"],
                status=official_analysis["status"],
                inputs_json_str=json.dumps({
                    "producer": producer_current,
                    "cepea": MOCK_CEPEA_DATA,
                    "b3": MOCK_B3_DATA
                }),
                recommendations=official_analysis["recommendations"]
            )
            st.success(f"Snapshot gravado com ID: {official_analysis['analysisId']}")
            
    with col_btn2:
        # Botão para gerar e baixar PDF
        pdf_filename = f"/workspace/scratch/{official_analysis['analysisId']}.pdf"
        generate_report_pdf(official_analysis, pdf_filename)
        with open(pdf_filename, "rb") as f:
            st.download_button(
                label="📥 Baixar Relatório PDF de Auditoria",
                data=f,
                file_name=f"Relatorio_{official_analysis['analysisId']}.pdf",
                mime="application/pdf"
            )

    st.write("---")

    # CARDS DE RESUMO DO MVP (Passo 35)
    st.subheader("Painel de Indicadores Principais")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    best_fut_symbol = official_analysis["bestFutureContract"]["symbol"] if official_analysis["bestFutureContract"] else "N/A"
    best_fut_price = official_analysis["bestFutureContract"]["effectivePrice"] if official_analysis["bestFutureContract"] else 0.0
    best_margin = official_analysis["bestFutureContract"]["marginOverCt"] if official_analysis["bestFutureContract"] else 0.0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">PREÇO SPOT CEPEA</div>
            <div class="metric-value">R$ {official_analysis['spot']['price']:.2f}</div>
            <div class="metric-sub">Ref: {official_analysis['spot']['referenceDate']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">MELHOR FUTURO (B3)</div>
            <div class="metric-value">{best_fut_symbol}</div>
            <div class="metric-sub">Efetivo: R$ {best_fut_price:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">CUSTO TOTAL (CT)</div>
            <div class="metric-value" style="color: #ef4444;">R$ {official_analysis['costs']['ctPerBag']:.2f}</div>
            <div class="metric-sub">Breakeven: R$ {official_analysis['costs']['financialBreakEvenPerBag']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">MELHOR MARGEM CT</div>
            <div class="metric-value" style="color: {'#10b981' if best_margin > 0 else '#ef4444'};">R$ {best_margin:+.2f}</div>
            <div class="metric-sub">Saca de 60 kg</div>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">ESTOQUE ATUAL</div>
            <div class="metric-value">{official_analysis['costs']['financialBreakEvenPerBag']:.0f} sc</div>
            <div class="metric-sub" style="color: #3b82f6;">Disponível Imediato</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # PLANO DE AÇÃO E RESPOSTAS AO PRODUTOR (Passo 34)
    st.subheader("💡 Plano de Ação Recomendado")
    if not official_analysis["recommendations"]:
        st.warning("⚠️ Nenhuma oportunidade de comercialização identificada. A recomendação é **AGUARDAR** e monitorar as margens futuras.")
    else:
        for idx, rec in enumerate(official_analysis["recommendations"], 1):
            with st.chat_message("assistant" if rec["type"] == "SPOT_SALE" else "user"):
                if rec["type"] == "SPOT_SALE":
                    st.markdown(f"**RECOMENDAÇÃO {idx}: VENDA SPOT (FÍSICO)**")
                    st.write(f"Recomendamos vender **{rec['quantityBags']:,}** sacas no mercado spot físico para suprir as necessidades de caixa previstas para **{rec['resourceNeedMonth']}**.")
                    st.write(f"**Preço de Liquidação:** R$ {rec['pricePerBag']:.2f}/saca | **Receita Gerada:** R$ {rec['estimatedRevenue']:.2f}")
                else:
                    st.markdown(f"**RECOMENDAÇÃO {idx}: HEDGE FUTURO (CONTRATO {rec['contract']})**")
                    st.write(f"Recomendamos abrir proteção de preço de **{rec['contracts']} contratos cheios B3** ({rec['quantityBags']:,} sacas) vinculados à necessidade de **{rec['resourceNeedMonth']}**.")
                    st.write(f"**Preço Efetivo Alvo:** R$ {rec['effectivePricePerBag']:.2f}/saca | **Receita Protegida:** R$ {rec['estimatedProtectedRevenue']:.2f} | **Margem CT:** +R$ {rec['marginOverCtPerBag']:.2f}/sc")
                st.caption(f"*Justificativa Técnica:* {rec['reason']}")

    st.write("---")

    # COMPARAÇÃO DE MERCADO (Tabela Passo 36)
    st.subheader("📊 Comparação Detalhada de Margens por Alternativa")
    st.write("As alternativas de mercado são comparadas de forma uniforme trazendo todos os preços para o valor líquido recebido na fazenda.")
    
    comparativo_rows = []
    # Inserir Spot
    comparativo_rows.append({
        "Alternativa": "Mercado Spot (CEPEA)",
        "Preço de Tela": f"R$ {official_analysis['spot']['price']:.2f}",
        "Preço Efetivo (Na Fazenda)": f"R$ {official_analysis['spot']['price']:.2f}",
        "Margem COE": f"R$ {official_analysis['spot']['margins']['overCoe']:+.2f}",
        "Margem COT": f"R$ {official_analysis['spot']['margins']['overCot']:+.2f}",
        "Margem CT (Econômica)": f"R$ {official_analysis['spot']['margins']['overCt']:+.2f}",
        "Status": "Disponível Imediato"
    })
    
    # Inserir Contratos Futuros
    for fut in official_analysis["futures"]:
        is_best = fut["symbol"] == best_fut_symbol
        comparativo_rows.append({
            "Alternativa": f"Contrato B3 {fut['symbol']} ({fut['expirationMonth']})",
            "Preço de Tela": f"R$ {fut['marketPrice']:.2f}",
            "Preço Efetivo (Na Fazenda)": f"R$ {fut['effectivePrice']:.2f}",
            "Margem COE": f"R$ {fut['margins']['overCoe']:+.2f}",
            "Margem COT": f"R$ {fut['margins']['overCot']:+.2f}",
            "Margem CT (Econômica)": f"R$ {fut['margins']['overCt']:+.2f}",
            "Status": "⭐ Melhor Margem Futura" if is_best else "Elegível"
        })
        
    df_comp = pd.DataFrame(comparativo_rows)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    st.write("---")

    # MEMÓRIA DE CÁLCULO EXPANSÍVEL (Passo 39)
    st.subheader("🔍 Memória de Cálculo para Auditoria")
    with st.expander("Clique aqui para ver a fórmula e o passo a passo matemático"):
        st.markdown("""
        **Fórmulas Utilizadas:**
        1. **Preço Efetivo do Futuro:**
           $$Preço\\ Efetivo = Cotação\\ B3 + Base\\ Esperada - Custo\\ Operacional$$
           $$R$ 77,30 + (-R$ 3,00) - R$ 0,20 = R$ 74,10$$
        2. **Cálculo da Margem Econômica (CT):**
           $$Margem\\ CT = Preço\\ Efetivo - Custo\\ Total\\ (CT)$$
           $$R$ 74,10 - R$ 66,80 = +R$ 7,30$$
        3. **Arredondamento para Contratos Inteiros da B3 (Tamanho do Contrato = 450 sacas):**
           $$Contratos\\ Necessários = \\lceil \\frac{Necessidade\\ Financeira}{Preço\\ Efetivo} \\times \\frac{1}{450} \\rceil$$
        """)
        
        st.json(official_analysis)

# ----------------- ABA 2: SIMULADOR INTERATIVO -----------------
with tab_sim:
    st.subheader("🧪 Simulador de Cenários Estressados (E se...?)")
    st.write("Simule flutuações e alterações rápidas de mercado sem gravar dados na análise oficial diária do banco de dados.")
    
    col_sim1, col_sim2 = st.columns([1, 1])
    
    with col_sim1:
        st.markdown("**Variáveis do Mercado**")
        sim_spot_price = st.slider("Preço Spot CEPEA (R$/saca)", min_value=50.0, max_value=100.0, value=70.0, step=0.50)
        sim_b3_price = st.slider("Preço Futuro CCMX26 na B3 (R$/saca)", min_value=50.0, max_value=100.0, value=77.30, step=0.50)
        sim_basis = st.slider("Base Esperada (R$/saca)", min_value=-10.0, max_value=5.0, value=-3.0, step=0.25)
        sim_b3_cost = st.slider("Custo Operacional B3 (R$/saca)", min_value=0.0, max_value=2.0, value=0.20, step=0.05)
        
    with col_sim2:
        st.markdown("**Variáveis de Custo da Fazenda**")
        sim_ct = st.slider("Custo Total (CT) (R$/saca)", min_value=40.0, max_value=90.0, value=66.80, step=0.50)
        
        # Calcular simulação em tempo real
        sim_effective_spot = sim_spot_price
        sim_effective_future = round(sim_b3_price + sim_basis - sim_b3_cost, 2)
        
        margin_spot_sim = round(sim_effective_spot - sim_ct, 2)
        margin_future_sim = round(sim_effective_future - sim_ct, 2)
        
        # Obter valores oficiais para comparativo
        official_effective_spot = official_analysis["spot"]["price"]
        official_effective_future = official_analysis["bestFutureContract"]["effectivePrice"] if official_analysis["bestFutureContract"] else 0.0
        official_margin_spot = official_analysis["spot"]["margins"]["overCt"]
        official_margin_future = official_analysis["bestFutureContract"]["marginOverCt"] if official_analysis["bestFutureContract"] else 0.0
        
        st.markdown("---")
        st.markdown("**Resultados Comparativos (Simulado vs. Oficial)**")
        
        # Construir tabela comparativa
        sim_data = {
            "Métrica": ["Preço Efetivo Spot", "Margem Spot (CT)", "Preço Efetivo Futuro", "Margem Futuro (CT)"],
            "Oficial": [f"R$ {official_effective_spot:.2f}", f"R$ {official_margin_spot:+.2f}", f"R$ {official_effective_future:.2f}", f"R$ {official_margin_future:+.2f}"],
            "Simulado": [f"R$ {sim_effective_spot:.2f}", f"R$ {margin_spot_sim:+.2f}", f"R$ {sim_effective_future:.2f}", f"R$ {margin_future_sim:+.2f}"]
        }
        st.table(pd.DataFrame(sim_data))

# ----------------- ABA 3: HISTÓRICO DE AUDITORIA -----------------
with tab_history:
    st.subheader("🗄️ Histórico de Análises Realizadas (Snapshots)")
    st.write("Cada análise oficial gravada no banco relacional de auditoria serve como um registro imutável do momento da decisão.")
    
    # Consultar banco de dados
    history = get_all_analyses()
    if not history:
        st.info("Nenhuma análise gravada no banco de dados ainda. Clique no botão 'Executar e Gravar Snapshot' na aba Principal para iniciar.")
    else:
        df_hist = pd.DataFrame(history)
        st.dataframe(df_hist, use_container_width=True)
