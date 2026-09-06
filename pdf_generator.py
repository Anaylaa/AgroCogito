from fpdf import FPDF
from datetime import datetime


# ============================================================
# PALETA AGROCOGITO
# ============================================================

GREEN_DARK = (21, 71, 52)          # #154734
GREEN = (72, 104, 62)              # verde secundário
GREEN_LIGHT = (222, 233, 211)      # verde muito claro

MAIZE = (242, 201, 76)             # #F2C94C
GOLD = (217, 164, 65)              # dourado
MAIZE_LIGHT = (252, 241, 190)      # amarelo suave

CREAM = (248, 245, 232)             # fundo dos cards
OFF_WHITE = (252, 251, 247)         # fundo geral
WHITE = (255, 255, 255)

TEXT = (41, 51, 45)                 # grafite
TEXT_LIGHT = (101, 112, 104)        # cinza
BORDER = (224, 226, 218)

RED = (164, 63, 63)
ORANGE = (183, 116, 34)


# ============================================================
# CLASSE PRINCIPAL
# ============================================================

class AgroCogitoPDF(FPDF):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_margins(10, 28, 10)
        self.set_auto_page_break(auto=True, margin=25)

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    def header(self):

        # Barra superior verde
        self.set_fill_color(*GREEN_DARK)
        self.rect(0, 0, 210, 20, "F")

        # Pequeno detalhe dourado
        self.set_fill_color(*MAIZE)
        self.rect(0, 18, 210, 2, "F")

        # Nome do produto
        self.set_xy(10, 5)

        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*WHITE)

        self.cell(
            0,
            6,
            "AGROCOGITO",
            align="L"
        )

        # Subtítulo
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(220, 230, 220)

        self.set_xy(10, 11)

        self.cell(
            0,
            4,
            "Corn Marketing & Hedge Service",
            align="L"
        )

        # Indicador visual no canto direito
        self.set_fill_color(*MAIZE)
        self.ellipse(192, 6, 6, 6, "F")

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    def footer(self):

        self.set_y(-20)

        # Linha
        self.set_draw_color(*BORDER)
        self.line(10, self.get_y(), 200, self.get_y())

        self.ln(3)

        self.set_font("Helvetica", "", 7)
        self.set_text_color(*TEXT_LIGHT)

        self.cell(
            145,
            4,
            "AgroCogito | Documento de apoio à decisão",
            align="L"
        )

        self.cell(
            45,
            4,
            f"Página {self.page_no()}",
            align="R"
        )

    # ========================================================
    # UTILITÁRIOS DE DESIGN
    # ========================================================

    def section_title(self, number, title):

        self.ln(2)

        # Número em amarelo
        self.set_fill_color(*MAIZE)

        self.rounded_rect(
            10,
            self.get_y(),
            10,
            8,
            2,
            "F"
        )

        self.set_xy(10, self.get_y() + 1)

        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*GREEN_DARK)

        self.cell(
            10,
            6,
            str(number),
            align="C"
        )

        # Título
        self.set_xy(24, self.get_y())

        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*GREEN_DARK)

        self.cell(
            0,
            8,
            title,
            ln=True
        )

        # Linha de apoio
        self.set_draw_color(*MAIZE)
        self.set_line_width(0.5)

        self.line(
            24,
            self.get_y(),
            200,
            self.get_y()
        )

        self.ln(4)

    def card(self, x, y, w, h, fill=WHITE):

        self.set_fill_color(*fill)
        self.set_draw_color(*BORDER)
        self.set_line_width(0.3)

        self.rounded_rect(
            x,
            y,
            w,
            h,
            3,
            "DF"
        )

    def label_value(self, x, y, label, value, width):

        self.set_xy(x, y)

        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(*TEXT_LIGHT)

        self.cell(
            width,
            4,
            label.upper()
        )

        self.set_xy(x, y + 5)

        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*TEXT)

        self.cell(
            width,
            5,
            value
        )

    def status_badge(self, status):

        status_config = {
            "OPPORTUNITY": (
                (224, 240, 222),
                GREEN_DARK,
                "OPORTUNIDADE"
            ),
            "PARTIAL": (
                (252, 240, 203),
                ORANGE,
                "OPORTUNIDADE PARCIAL"
            ),
            "WAIT": (
                (242, 231, 225),
                RED,
                "AGUARDAR"
            )
        }

        bg, color, label = status_config.get(
            status,
            (CREAM, TEXT_LIGHT, status)
        )

        x = 148
        y = self.get_y() - 1
        w = 52
        h = 9

        self.set_fill_color(*bg)

        self.rounded_rect(
            x,
            y,
            w,
            h,
            4,
            "F"
        )

        self.set_xy(x, y + 2)

        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*color)

        self.cell(
            w,
            5,
            label,
            align="C"
        )

    def money(self, value):

        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ============================================================
# GERAÇÃO DO RELATÓRIO
# ============================================================

def generate_report_pdf(analysis_data, output_path):

    pdf = AgroCogitoPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.add_page()

    # ========================================================
    # CAPA / IDENTIFICAÇÃO
    # ========================================================

    pdf.set_y(30)

    # Pequena etiqueta
    pdf.set_fill_color(*MAIZE_LIGHT)

    pdf.rounded_rect(
        10,
        pdf.get_y(),
        42,
        7,
        3,
        "F"
    )

    pdf.set_xy(10, pdf.get_y() + 1.5)

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*GREEN_DARK)

    pdf.cell(
        42,
        4,
        "RELATÓRIO EXECUTIVO",
        align="C"
    )

    pdf.ln(12)

    # Título
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*GREEN_DARK)

    pdf.multi_cell(
        0,
        9,
        "Relatório de\nComercialização e Proteção"
    )

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*TEXT_LIGHT)

    pdf.cell(
        0,
        6,
        "Análise de mercado, margem econômica e estratégias de hedge",
        ln=True
    )

    pdf.ln(8)

    # ========================================================
    # CARD DE IDENTIFICAÇÃO
    # ========================================================

    y = pdf.get_y()

    pdf.card(
        10,
        y,
        190,
        37,
        CREAM
    )

    pdf.label_value(
        17,
        y + 7,
        "Produtor",
        f"{analysis_data['producerName']}",
        70
    )

    pdf.label_value(
        17,
        y + 22,
        "ID do produtor",
        str(analysis_data["producerId"]),
        70
    )

    pdf.label_value(
        95,
        y + 7,
        "Commodity",
        "Milho",
        45
    )

    pdf.label_value(
        95,
        y + 22,
        "ID da análise",
        str(analysis_data["analysisId"]),
        45
    )

    pdf.label_value(
        150,
        y + 7,
        "Gerado em",
        str(analysis_data["generatedAt"]),
        40
    )

    pdf.ln(48)

    # ========================================================
    # 1. IDENTIFICAÇÃO
    # ========================================================

    pdf.section_title(
        1,
        "Identificação Geral"
    )

    pdf.card(
        10,
        pdf.get_y(),
        190,
        25,
        WHITE
    )

    y = pdf.get_y()

    pdf.label_value(
        17,
        y + 6,
        "Produtor",
        f"{analysis_data['producerName']} ({analysis_data['producerId']})",
        105
    )

    pdf.label_value(
        125,
        y + 6,
        "Commodity",
        f"{analysis_data['commodity']} (Milho)",
        60
    )

    pdf.ln(32)

    # ========================================================
    # 2. CUSTOS
    # ========================================================

    pdf.section_title(
        2,
        "Custos e Referências Econômicas"
    )

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*TEXT_LIGHT)

    pdf.cell(
        0,
        4,
        "Valores expressos por saca de 60 kg.",
        ln=True
    )

    pdf.ln(3)

    costs = analysis_data["costs"]

    y = pdf.get_y()

    # Três cards
    card_width = 59

    cards = [
        (
            "COE",
            "Operacional Efetivo",
            pdf.money(costs["coePerBag"])
        ),
        (
            "COT",
            "Operacional Total",
            pdf.money(costs["cotPerBag"])
        ),
        (
            "CT",
            "Custo Total",
            pdf.money(costs["ctPerBag"])
        )
    ]

    for i, (title, subtitle, value) in enumerate(cards):

        x = 10 + i * 65

        pdf.card(
            x,
            y,
            card_width,
            30,
            CREAM
        )

        pdf.set_xy(x + 5, y + 5)

        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*GREEN)

        pdf.cell(
            card_width - 10,
            4,
            title
        )

        pdf.set_xy(x + 5, y + 11)

        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*TEXT_LIGHT)

        pdf.cell(
            card_width - 10,
            4,
            subtitle
        )

        pdf.set_xy(x + 5, y + 18)

        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*TEXT)

        pdf.cell(
            card_width - 10,
            6,
            value
        )

    pdf.ln(37)

    # Break-even
    y = pdf.get_y()

    pdf.set_fill_color(*GREEN_DARK)

    pdf.rounded_rect(
        10,
        y,
        190,
        17,
        3,
        "F"
    )

    pdf.set_xy(17, y + 4)

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*MAIZE)

    pdf.cell(
        105,
        4,
        "PONTO DE EQUILÍBRIO FINANCEIRO PLANEJADO"
    )

    pdf.set_xy(130, y + 3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*WHITE)

    pdf.cell(
        63,
        7,
        f"{pdf.money(costs['financialBreakEvenPerBag'])} / saca",
        align="R"
    )

    pdf.ln(25)

    # ========================================================
    # 3. DIAGNÓSTICO
    # ========================================================

    pdf.section_title(
        3,
        "Diagnóstico do Sistema"
    )

    status = analysis_data["status"]

    # Card do status
    y = pdf.get_y()

    pdf.card(
        10,
        y,
        190,
        39,
        WHITE
    )

    pdf.set_xy(17, y + 7)

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*TEXT_LIGHT)

    pdf.cell(
        40,
        5,
        "STATUS ATUAL"
    )

    pdf.set_xy(17, y + 14)

    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(*GREEN_DARK)

    pdf.cell(
        120,
        7,
        status
    )

    pdf.set_xy(148, y + 7)

    pdf.status_badge(status)

    if status == "OPPORTUNITY":

        msg = (
            "Oportunidades de comercialização economicamente atrativas "
            "foram identificadas para cobrir as necessidades de caixa "
            "e fixar margens positivas."
        )

    elif status == "PARTIAL":

        msg = (
            "Parte das necessidades de caixa pode ser atendida com "
            "o estoque/produção elegíveis, mas não de forma integral "
            "para todos os meses."
        )

    elif status == "WAIT":

        msg = (
            "Nenhuma oportunidade de comercialização com margem "
            "econômica (CT) positiva foi encontrada hoje. "
            "A recomendação é AGUARDAR."
        )

    else:

        msg = "Status indefinido ou dados parciais."

    pdf.set_xy(17, y + 24)

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*TEXT)

    pdf.multi_cell(
        175,
        4,
        msg
    )

    pdf.ln(49)

    # ========================================================
    # 4. PLANO DE AÇÃO
    # ========================================================

    pdf.section_title(
        4,
        "Plano de Ação Recomendado"
    )

    recs = analysis_data["recommendations"]

    if not recs:

        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(*TEXT_LIGHT)

        pdf.multi_cell(
            0,
            5,
            "Nenhuma operação recomendada para o momento "
            "(Aguardar melhora do mercado)."
        )

    else:

        for idx, r in enumerate(recs, 1):

            # ------------------------------------------------
            # Verifica espaço na página
            # ------------------------------------------------

            if pdf.get_y() > 235:

                pdf.add_page()

            y = pdf.get_y()

            pdf.card(
                10,
                y,
                190,
                58 if r["type"] == "SPOT_SALE" else 68,
                CREAM
            )

            # Cabeçalho da recomendação
            pdf.set_fill_color(*MAIZE)

            pdf.rounded_rect(
                17,
                y + 7,
                8,
                8,
                2,
                "F"
            )

            pdf.set_xy(17, y + 8)

            pdf.set_font("Helvetica", "B", 7)
            pdf.set_text_color(*GREEN_DARK)

            pdf.cell(
                8,
                5,
                str(idx),
                align="C"
            )

            pdf.set_xy(30, y + 7)

            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*GREEN_DARK)

            if r["type"] == "SPOT_SALE":

                title = "VENDA SPOT"
                subtitle = "Disponível imediato"

            else:

                title = "PROTEÇÃO FUTURA"
                subtitle = "Hedge B3 CCM"

            pdf.cell(
                90,
                5,
                title
            )

            pdf.set_xy(30, y + 13)

            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(*TEXT_LIGHT)

            pdf.cell(
                90,
                4,
                subtitle
            )

            # ------------------------------------------------
            # Conteúdo
            # ------------------------------------------------

            current_y = y + 25

            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(*TEXT)

            if r["type"] == "SPOT_SALE":

                lines = [
                    (
                        "Mês de Caixa",
                        str(r["resourceNeedMonth"])
                    ),
                    (
                        "Quantidade",
                        f"{r['quantityBags']} sacas"
                    ),
                    (
                        "Preço CEPEA",
                        f"{pdf.money(r['pricePerBag'])}/saca"
                    ),
                    (
                        "Receita Bruta",
                        pdf.money(r["estimatedRevenue"])
                    )
                ]

            else:

                lines = [
                    (
                        "Mês de Caixa",
                        str(r["resourceNeedMonth"])
                    ),
                    (
                        "Contrato",
                        str(r["contract"])
                    ),
                    (
                        "Contratos B3",
                        f"{r['contracts']} contratos inteiros (450 sc/cada)"
                    ),
                    (
                        "Quantidade",
                        f"{r['quantityBags']} sacas protegidas"
                    ),
                    (
                        "Preço Efetivo",
                        f"{pdf.money(r['effectivePricePerBag'])}/saca"
                    ),
                    (
                        "Receita Protegida",
                        pdf.money(r["estimatedProtectedRevenue"])
                    ),
                    (
                        "Margem sobre CT",
                        f"+{pdf.money(r['marginOverCtPerBag'])}/saca"
                    )
                ]

            left_x = 18
            right_x = 108

            for i, (label, value) in enumerate(lines):

                if i % 2 == 0:

                    x = left_x
                    row = i // 2

                else:

                    x = right_x
                    row = i // 2

                yy = current_y + row * 9

                pdf.set_xy(x, yy)

                pdf.set_font("Helvetica", "B", 7)
                pdf.set_text_color(*TEXT_LIGHT)

                pdf.cell(
                    40,
                    4,
                    label.upper()
                )

                pdf.set_xy(x, yy + 4)

                pdf.set_font("Helvetica", "B", 8.5)
                pdf.set_text_color(*TEXT)

                pdf.cell(
                    78,
                    4,
                    str(value)
                )

            # ------------------------------------------------
            # Justificativa
            # ------------------------------------------------

            justification_y = y + (
                48 if r["type"] == "SPOT_SALE" else 58
            )

            pdf.set_xy(18, justification_y)

            pdf.set_font("Helvetica", "I", 7.5)
            pdf.set_text_color(*TEXT_LIGHT)

            pdf.multi_cell(
                175,
                3.5,
                f"Justificativa: {r['reason']}"
            )

            pdf.set_y(
                y + (63 if r["type"] == "SPOT_SALE" else 73)
            )

    # ========================================================
    # 5. MEMÓRIA DE CÁLCULO
    # ========================================================

    if pdf.get_y() > 215:

        pdf.add_page()

    pdf.section_title(
        5,
        "Memória de Cálculo para Auditoria"
    )

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*TEXT_LIGHT)

    pdf.multi_cell(
        0,
        4,
        "Comparativo entre alternativas de comercialização, "
        "preços efetivos e margens econômicas."
    )

    pdf.ln(4)

    # --------------------------------------------------------
    # TABELA
    # --------------------------------------------------------

    table_x = 10
    table_y = pdf.get_y()

    col_widths = [
        29,
        29,
        29,
        26,
        26,
        26,
        25
    ]

    headers = [
        "Alternativa",
        "Preço\nB3/CEPEA",
        "Preço\nEfetivo",
        "Margem\nCOE",
        "Margem\nCOT",
        "Margem\nCT",
        "Risco\nBase"
    ]

    # Cabeçalho
    pdf.set_fill_color(*GREEN_DARK)
    pdf.set_text_color(*WHITE)
    pdf.set_font("Helvetica", "B", 7)

    for width, header in zip(col_widths, headers):

        pdf.cell(
            width,
            10,
            header,
            border=0,
            align="C",
            fill=True
        )

    pdf.ln()

    # --------------------------------------------------------
    # Linha SPOT
    # --------------------------------------------------------

    spot = analysis_data["spot"]

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*TEXT)

    pdf.set_fill_color(*CREAM)

    spot_values = [
        "Mercado Spot",
        pdf.money(spot["price"]),
        pdf.money(spot["price"]),
        f"{spot['margins']['overCoe']:+.2f}",
        f"{spot['margins']['overCot']:+.2f}",
        f"{spot['margins']['overCt']:+.2f}",
        "N/A"
    ]

    for width, value in zip(col_widths, spot_values):

        pdf.cell(
            width,
            8,
            value,
            border=1,
            align="C",
            fill=True
        )

    pdf.ln()

    # --------------------------------------------------------
    # FUTUROS
    # --------------------------------------------------------

    for i, future in enumerate(analysis_data["futures"]):

        if i % 2 == 0:
            pdf.set_fill_color(*WHITE)
        else:
            pdf.set_fill_color(*CREAM)

        values = [
            future["symbol"],
            pdf.money(future["marketPrice"]),
            pdf.money(future["effectivePrice"]),
            f"{future['margins']['overCoe']:+.2f}",
            f"{future['margins']['overCot']:+.2f}",
            f"{future['margins']['overCt']:+.2f}",
            (
                f"{future['basisScenario']['lower']:.1f}"
                f" a "
                f"{future['basisScenario']['upper']:.1f}"
            )
        ]

        for width, value in zip(col_widths, values):

            pdf.cell(
                width,
                8,
                str(value),
                border=1,
                align="C",
                fill=True
            )

        pdf.ln()

    pdf.ln(7)

    # --------------------------------------------------------
    # LEGENDA
    # --------------------------------------------------------

    pdf.set_fill_color(*MAIZE_LIGHT)

    pdf.rounded_rect(
        10,
        pdf.get_y(),
        190,
        20,
        3,
        "F"
    )

    pdf.set_xy(17, pdf.get_y() + 5)

    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(*GREEN_DARK)

    pdf.cell(
        35,
        4,
        "LEITURA DA TABELA"
    )

    pdf.set_xy(17, pdf.get_y() + 6)

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(*TEXT)

    pdf.multi_cell(
        175,
        4,
        "Margens positivas indicam preço efetivo acima do respectivo "
        "nível de custo. A faixa de risco de base representa o cenário "
        "considerado para a diferença entre preço futuro e mercado físico."
    )

    pdf.ln(10)

    # ========================================================
    # 6. AVISOS LEGAIS
    # ========================================================

    if pdf.get_y() > 220:

        pdf.add_page()

    pdf.section_title(
        6,
        "Termos e Avisos Legais"
    )

    # Caixa de aviso
    y = pdf.get_y()

    pdf.set_fill_color(*CREAM)

    pdf.rounded_rect(
        10,
        y,
        190,
        43,
        3,
        "F"
    )

    # Barra lateral
    pdf.set_fill_color(*MAIZE)

    pdf.rect(
        10,
        y,
        4,
        43,
        "F"
    )

    pdf.set_xy(20, y + 7)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*GREEN_DARK)

    pdf.cell(
        165,
        5,
        "AVISO IMPORTANTE"
    )

    pdf.set_xy(20, y + 16)

    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(*TEXT)

    pdf.multi_cell(
        165,
        4.5,
        analysis_data["disclaimer"]
    )

    pdf.ln(12)

    # Disclaimer fixo
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(*TEXT_LIGHT)

    pdf.multi_cell(
        190,
        4,
        "Esta análise possui caráter exclusivamente informativo e "
        "constitui ferramenta de apoio à decisão. Os valores podem "
        "sofrer alterações e não representam garantia de resultado."
    )

    # ========================================================
    # SALVAR
    # ========================================================

    pdf.output(output_path)