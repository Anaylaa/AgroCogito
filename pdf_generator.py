from fpdf import FPDF
import datetime

class AgroCogitoPDF(FPDF):
    def header(self):
        # Desenhar uma barra superior institucional azul escuro
        self.set_fill_color(24, 43, 73)
        self.rect(0, 0, 210, 15, "F")
        
        self.set_y(4)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, "AgroCogito MVP — Corn Marketing & Hedge Service", align="C", ln=True)
        self.ln(5)

    def footer(self):
        self.set_y(-25)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        # Disclaimer curto de rodapé
        self.multi_cell(0, 3, "Aviso: Esta análise possui caráter exclusivamente informativo e constitui ferramenta de apoio à decisão. Os valores podem sofrer alterações e não representam garantia de resultado.", align="C")
        self.ln(2)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generate_report_pdf(analysis_data, output_path):
    """
    Gera um relatório PDF corporativo e elegante com base nos resultados da análise oficial.
    Atende aos 26 itens de auditoria descritos no critério de aceite (Passo 43).
    """
    pdf = AgroCogitoPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=30)
    pdf.set_text_color(33, 33, 33)
    
    # Título do Relatório
    pdf.set_y(25)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 10, "Relatório de Comercialização e Proteção (Hedge)", ln=True)
    
    # Metadata da Análise
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(100, 6, f"ID da Análise: {analysis_data['analysisId']}", ln=False)
    pdf.cell(0, 6, f"Gerado em: {analysis_data['generatedAt']}", ln=True, align="R")
    pdf.ln(2)
    
    # Linha divisória
    pdf.set_draw_color(220, 220, 220)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    
    # 1. Identificação do Produtor e Commodity
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 6, "1. Identificação Geral", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(33, 33, 33)
    pdf.cell(90, 6, f"Produtor: {analysis_data['producerName']} ({analysis_data['producerId']})", ln=False)
    pdf.cell(0, 6, f"Commodity: {analysis_data['commodity']} (Milho)", ln=True)
    pdf.ln(3)

    # 2. Custos de Produção e Ponto de Equilíbrio
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 6, "2. Custos e Referências Econômicas (por saca de 60 kg)", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(33, 33, 33)
    
    costs = analysis_data["costs"]
    pdf.cell(63, 6, f"COE (Operacional Efetivo): R$ {costs['coePerBag']:.2f}", ln=False)
    pdf.cell(63, 6, f"COT (Operacional Total): R$ {costs['cotPerBag']:.2f}", ln=False)
    pdf.cell(0, 6, f"CT (Custo Total): R$ {costs['ctPerBag']:.2f}", ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, f"Ponto de Equilíbrio Financeiro Planejado: R$ {costs['financialBreakEvenPerBag']:.2f}/saca", ln=True)
    pdf.ln(3)

    # 3. Resumo da Análise e Status Geral
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 6, f"3. Diagnóstico do Sistema: STATUS {analysis_data['status']}", ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(33, 33, 33)
    if analysis_data["status"] == "OPPORTUNITY":
        msg = "Oportunidades de comercialização economicamente atrativas foram identificadas para cobrir as necessidades de caixa e fixar margens positivas."
    elif analysis_data["status"] == "PARTIAL":
        msg = "Parte das necessidades de caixa pode ser atendida com o estoque/produção elegíveis, mas não de forma integral para todos os meses."
    elif analysis_data["status"] == "WAIT":
        msg = "Nenhuma oportunidade de comercialização com margem econômica (CT) positiva foi encontrada hoje. A recomendação é AGUARDAR."
    else:
        msg = "Status indefinido ou dados parciais."
    pdf.multi_cell(0, 5, msg)
    pdf.ln(3)

    # 4. Recomendações de Comercialização e Proteção
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 6, "4. Plano de Ação Recomendado", ln=True)
    
    recs = analysis_data["recommendations"]
    if not recs:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, "Nenhuma operação recomendada para o momento (Aguardar melhora do mercado).", ln=True)
    else:
        for idx, r in enumerate(recs, 1):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(46, 117, 89) # Verde Escuro
            
            if r["type"] == "SPOT_SALE":
                pdf.cell(0, 6, f"RECOMENDAÇÃO {idx}: VENDA SPOT (Disponível Imediato)", ln=True)
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(33, 33, 33)
                pdf.cell(0, 5, f" - Mês de Caixa Alvo: {r['resourceNeedMonth']}", ln=True)
                pdf.cell(0, 5, f" - Quantidade: {r['quantityBags']} sacas no mercado spot físico", ln=True)
                pdf.cell(0, 5, f" - Preço de Venda (CEPEA): R$ {r['pricePerBag']:.2f}/saca", ln=True)
                pdf.cell(0, 5, f" - Receita Bruta Estimada: R$ {r['estimatedRevenue']:.2f}", ln=True)
                pdf.set_font("Helvetica", "I", 9)
                pdf.multi_cell(0, 4, f" - Justificativa: {r['reason']}")
            else:
                pdf.cell(0, 6, f"RECOMENDAÇÃO {idx}: PROTEÇÃO FUTURA (Hedge B3 CCM)", ln=True)
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(33, 33, 33)
                pdf.cell(0, 5, f" - Mês de Caixa Alvo: {r['resourceNeedMonth']}", ln=True)
                pdf.cell(0, 5, f" - Contrato Futuro Utilizado: {r['contract']} (Vencimento B3)", ln=True)
                pdf.cell(0, 5, f" - Número de Contratos da B3: {r['contracts']} contratos inteiros (450 sc/cada)", ln=True)
                pdf.cell(0, 5, f" - Quantidade Total: {r['quantityBags']} sacas protegidas", ln=True)
                pdf.cell(0, 5, f" - Preço Efetivo Estimado: R$ {r['effectivePricePerBag']:.2f}/saca (Cotação com Base e Custo deduzidos)", ln=True)
                pdf.cell(0, 5, f" - Receita Protegida de Referência: R$ {r['estimatedProtectedRevenue']:.2f}", ln=True)
                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(0, 5, f" - Margem Econômica Estimada sobre CT: +R$ {r['marginOverCtPerBag']:.2f}/saca", ln=True)
                pdf.set_font("Helvetica", "I", 9)
                pdf.multi_cell(0, 4, f" - Justificativa: {r['reason']}")
            pdf.ln(2)

    # 5. Memória de Cálculo Detalhada (Preços Efetivos e Margens)
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 6, "5. Memória de Cálculo para Auditoria", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(33, 33, 33)
    
    # Cabeçalho da Tabela
    pdf.set_fill_color(230, 235, 245)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(30, 6, "Alternativa", 1, 0, "C", True)
    pdf.cell(28, 6, "Preço B3/CEPEA", 1, 0, "C", True)
    pdf.cell(28, 6, "Preço Efetivo", 1, 0, "C", True)
    pdf.cell(26, 6, "Margem COE", 1, 0, "C", True)
    pdf.cell(26, 6, "Margem COT", 1, 0, "C", True)
    pdf.cell(26, 6, "Margem CT", 1, 0, "C", True)
    pdf.cell(26, 6, "Faixa Risco Base", 1, 1, "C", True)
    
    # Dados Spot
    pdf.set_font("Helvetica", "", 9)
    spot = analysis_data["spot"]
    pdf.cell(30, 5, "Mercado Spot", 1, 0, "L")
    pdf.cell(28, 5, f"R$ {spot['price']:.2f}", 1, 0, "C")
    pdf.cell(28, 5, f"R$ {spot['price']:.2f}", 1, 0, "C")
    pdf.cell(26, 5, f"+R$ {spot['margins']['overCoe']:.2f}", 1, 0, "C")
    pdf.cell(26, 5, f"+R$ {spot['margins']['overCot']:.2f}", 1, 0, "C")
    pdf.cell(26, 5, f"+R$ {spot['margins']['overCt']:.2f}", 1, 0, "C")
    pdf.cell(26, 5, "N/A", 1, 1, "C")
    
    # Dados de cada futuro
    for f in analysis_data["futures"]:
        pdf.cell(30, 5, f["symbol"], 1, 0, "L")
        pdf.cell(28, 5, f"R$ {f['marketPrice']:.2f}", 1, 0, "C")
        pdf.cell(28, 5, f"R$ {f['effectivePrice']:.2f}", 1, 0, "C")
        pdf.cell(26, 5, f"+R$ {f['margins']['overCoe']:.2f}", 1, 0, "C")
        pdf.cell(26, 5, f"+R$ {f['margins']['overCot']:.2f}", 1, 0, "C")
        pdf.cell(26, 5, f"+R$ {f['margins']['overCt']:.2f}", 1, 0, "C")
        pdf.cell(26, 5, f"{f['basisScenario']['lower']:.1f} a {f['basisScenario']['upper']:.1f}", 1, 1, "C")
        
    pdf.ln(4)
    
    # 6. Aviso Legal e de Apoio à Decisão
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 5, "6. Termos e Avisos Legais", ln=True)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 4, analysis_data["disclaimer"])
    
    pdf.output(output_path)
