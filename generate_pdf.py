import os
import matplotlib
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# -------------------------------------------------------------------------
# Registro de Fonte Unicode TTF (DejaVu Sans)
# -------------------------------------------------------------------------
font_dir = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(font_dir, 'DejaVuSans.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', os.path.join(font_dir, 'DejaVuSans-Bold.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans-Oblique', os.path.join(font_dir, 'DejaVuSans-Oblique.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuSans-BoldOblique', os.path.join(font_dir, 'DejaVuSans-BoldOblique.ttf')))

registerFontFamily(
    'DejaVuSans',
    normal='DejaVuSans',
    bold='DejaVuSans-Bold',
    italic='DejaVuSans-Oblique',
    boldItalic='DejaVuSans-BoldOblique'
)

# -------------------------------------------------------------------------
# Custom Canvas para Numeração Dinâmica e Cabeçalhos Corridos
# -------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("DejaVuSans", 8)
        self.setFillColor(colors.HexColor("#555555"))
        
        # Não desenha cabeçalho/rodapé na capa (Página 1)
        if self._pageNumber > 1:
            # Running Header
            self.drawString(45, 752, "SISB110 — Ciência dos Dados e BI | Relatório Executivo: Saúde Mental Estudantil")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(45, 746, 567, 746)
            
            # Running Footer
            self.line(45, 42, 567, 42)
            self.drawString(45, 30, "UFAL / IC / Bacharelado em Sistemas de Informação — Bruno Martins Gomes")
            page_text = f"Página {self._pageNumber} de {page_count}"
            self.drawRightString(567, 30, page_text)
            
        self.restoreState()

def build_pdf():
    pdf_filename = "relatorio_executivo_bi.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=48,
        bottomMargin=48
    )

    # Cores do Sistema de Design
    primary_color = colors.HexColor("#1A365D")    # Dark Navy
    secondary_color = colors.HexColor("#2B6CB0")  # Slate Blue
    dark_neutral = colors.HexColor("#2D3748")     # Charcoal body text
    card_bg = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#CBD5E1")
    warning_bg = colors.HexColor("#FEF3C7")
    warning_border = colors.HexColor("#F59E0B")

    base_styles = getSampleStyleSheet()

    styles = {
        'CoverInstitution': ParagraphStyle(
            'CoverInstitution',
            parent=base_styles['Normal'],
            fontName='DejaVuSans-Bold',
            fontSize=9.5,
            leading=13,
            textColor=secondary_color,
            alignment=1,
            spaceAfter=3
        ),
        'CoverCourse': ParagraphStyle(
            'CoverCourse',
            parent=base_styles['Normal'],
            fontName='DejaVuSans',
            fontSize=8.5,
            leading=12,
            textColor=dark_neutral,
            alignment=1,
            spaceAfter=14
        ),
        'CoverTitle': ParagraphStyle(
            'CoverTitle',
            parent=base_styles['Normal'],
            fontName='DejaVuSans-Bold',
            fontSize=15,
            leading=19,
            textColor=primary_color,
            alignment=1,
            spaceAfter=5
        ),
        'CoverSubtitle': ParagraphStyle(
            'CoverSubtitle',
            parent=base_styles['Normal'],
            fontName='DejaVuSans',
            fontSize=9.5,
            leading=13.5,
            textColor=dark_neutral,
            alignment=1,
            spaceAfter=11
        ),
        'CoverAuthor': ParagraphStyle(
            'CoverAuthor',
            parent=base_styles['Normal'],
            fontName='DejaVuSans-Bold',
            fontSize=8.5,
            leading=12,
            textColor=primary_color,
            alignment=1,
            spaceAfter=13
        ),
        'ExecSummaryTitle': ParagraphStyle(
            'ExecSummaryTitle',
            parent=base_styles['Normal'],
            fontName='DejaVuSans-Bold',
            fontSize=10.5,
            leading=13.5,
            textColor=primary_color,
            spaceAfter=5
        ),
        'ExecSummaryBody': ParagraphStyle(
            'ExecSummaryBody',
            parent=base_styles['Normal'],
            fontName='DejaVuSans',
            fontSize=8.2,
            leading=11.2,
            textColor=dark_neutral,
            spaceAfter=4
        ),
        'H1': ParagraphStyle(
            'Heading1_Custom',
            parent=base_styles['Normal'],
            fontName='DejaVuSans-Bold',
            fontSize=12,
            leading=15,
            textColor=primary_color,
            spaceBefore=12,
            spaceAfter=5,
            keepWithNext=True
        ),
        'H2': ParagraphStyle(
            'Heading2_Custom',
            parent=base_styles['Normal'],
            fontName='DejaVuSans-Bold',
            fontSize=9.5,
            leading=12.5,
            textColor=secondary_color,
            spaceBefore=8,
            spaceAfter=3,
            keepWithNext=True
        ),
        'Body': ParagraphStyle(
            'Body_Custom',
            parent=base_styles['Normal'],
            fontName='DejaVuSans',
            fontSize=8.5,
            leading=11.8,
            textColor=dark_neutral,
            spaceAfter=5
        ),
        'Bullet': ParagraphStyle(
            'Bullet_Custom',
            parent=base_styles['Normal'],
            fontName='DejaVuSans',
            fontSize=8.2,
            leading=11.2,
            textColor=dark_neutral,
            leftIndent=12,
            firstLineIndent=-9,
            spaceAfter=2.5
        ),
        'TableText': ParagraphStyle(
            'TableText',
            parent=base_styles['Normal'],
            fontName='DejaVuSans',
            fontSize=7.2,
            leading=9.2,
            textColor=dark_neutral
        ),
        'TableTextBold': ParagraphStyle(
            'TableTextBold',
            parent=base_styles['Normal'],
            fontName='DejaVuSans-Bold',
            fontSize=7.2,
            leading=9.2,
            textColor=primary_color
        ),
        'TableHeader': ParagraphStyle(
            'TableHeader',
            parent=base_styles['Normal'],
            fontName='DejaVuSans-Bold',
            fontSize=7.2,
            leading=9.2,
            textColor=colors.white,
            alignment=1
        ),
        'Caption': ParagraphStyle(
            'Caption',
            parent=base_styles['Normal'],
            fontName='DejaVuSans-Oblique',
            fontSize=7.2,
            leading=9.5,
            textColor=colors.HexColor("#64748B"),
            alignment=1,
            spaceBefore=2.5,
            spaceAfter=6
        ),
        'CalloutText': ParagraphStyle(
            'CalloutText',
            parent=base_styles['Normal'],
            fontName='DejaVuSans',
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#1E3A8A")
        ),
        'GithubPlaceholder': ParagraphStyle(
            'GithubPlaceholder',
            parent=base_styles['Normal'],
            fontName='DejaVuSans-Bold',
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#92400E")
        )
    }

    story = []

    # =========================================================================
    # SEÇÃO 1: CAPA E RESUMO EXECUTIVO (PÁGINA 1 - ESTRITAMENTE 1 PÁGINA)
    # =========================================================================
    story.append(Paragraph("UNIVERSIDADE FEDERAL DE ALAGOAS (UFAL) • INSTITUTO DE COMPUTAÇÃO", styles['CoverInstitution']))
    story.append(Paragraph("SISB110 — Ciência dos Dados e Inteligência Empresarial • Bacharelado em Sistemas de Informação", styles['CoverCourse']))
    
    story.append(Paragraph("RELATÓRIO EXECUTIVO DE BUSINESS INTELLIGENCE:<br/>DETERMINANTES ASSOCIADOS À SAÚDE MENTAL ESTUDANTIL", styles['CoverTitle']))
    story.append(Paragraph("Evidências Descritivas, Inferenciais e Diretrizes de Ação para a Gestão Universitária", styles['CoverSubtitle']))
    story.append(Paragraph("Estudante: <b>Bruno Martins Gomes</b> • Docente / Disciplina: <b>SISB110 / UFAL</b> • Outubro / 2026", styles['CoverAuthor']))
    
    # Caixa Destacada do Resumo Executivo
    summary_html = [
        [Paragraph("<b>RESUMO EXECUTIVO (EXECUTIVE SUMMARY)</b>", styles['ExecSummaryTitle'])],
        [Paragraph(
            "<b>Contexto e Problema de Negócio:</b> A persistência do adoecimento psíquico e o risco de evasão na educação superior impõem à gestão universitária a necessidade de decisões alocativas baseadas em evidências empíricas. Este estudo analisa uma amostra transversal de <b>27.837 estudantes universitários</b> (derivada da versão integral de 27.901 registros do <i>Student Depression Dataset</i>, Kaggle/Hopesb) sob a ótica de Business Intelligence (BI) para apoio psicopedagógico e permanência estudantil.",
            styles['ExecSummaryBody']
        )],
        [Paragraph(
            "<b>Principais Achados Empíricos:</b><br/>"
            "• <b>Prevalência Amostral Estimada:</b> A proporção de estudantes com indicativo de depressão na população amostrada é de <b>58,52%</b> (IC 95% de Wilson: <b>[57,94%, 59,10%]</b>, margem de erro de ±0,58%).<br/>"
            "• <b>Vulnerabilidade Financeira como Maior Preditador Associativo:</b> O estresse financeiro exibe associação moderada (Cramér's <i>V</i> = 0,36) e <b>forte tendência linear monotônica</b> (Cochran-Armitage <i>Z</i> = 60,67, <i>p</i> &lt; 0,0001), com a taxa de depressão saltando de <b>31,81%</b> no nível 1 para <b>81,23%</b> no nível 5 (acréscimo de ~50 pontos percentuais).<br/>"
            "• <b>Sobrecarga Acadêmica:</b> Estudantes com indicativo de depressão reportam pressão percebida substancialmente superior (3,69 vs. 2,36; Mann-Whitney <i>U</i> = 1,45 × 10<sup>8</sup>, <i>p</i> &lt; 0,0001; <i>d</i> de Cohen = 1,10). A correlação bisserial por postos (<i>r<sub>rb</sub></i> = 0,5408) reflete uma <b>probabilidade de superioridade de aproximadamente 77%, contando empates pela metade</b>.<br/>"
            "• <b>Sono e Risco nos Extremos:</b> A privação severa (&lt; 5h/dia) registra a maior taxa (<b>64,51%</b>), enquanto sono prolongado (&gt; 8h) apresenta a menor (<b>50,86%</b>), com associação global fraca (<i>V</i> = 0,10) e não-monotônica (faixa 5–6h = 56,85% vs. 7–8h = 59,45%).<br/>"
            "• <b>Desconexão entre Notas e Satisfação:</b> O rendimento acadêmico (CGPA) não possui correlação prática substantiva com a satisfação com os estudos (Spearman <i>ρ</i> = -0,0467; <i>p</i> &lt; 0,0001, |<i>ρ</i>| &lt; 0,10).",
            styles['ExecSummaryBody']
        )],
        [Paragraph(
            "<b>Principal Recomendação Institucional:</b> Recomenda-se direcionamento orçamentário prioritário de auxílios e bolsas de permanência discente aos estudantes em vulnerabilidade financeira crítica (níveis 4 e 5), associado a diretrizes pedagógicas de escalonamento avaliativo para diluição dos picos de pressão curricular. Ações de suporte psicossocial não devem adotar o desempenho acadêmico (CGPA) como critério de elegibilidade ou triagem.",
            styles['ExecSummaryBody']
        )]
    ]
    
    summary_table = Table(summary_html, colWidths=[522])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), card_bg),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    
    # Quebra de página estrita após o resumo executivo (Capa + Resumo = Página 1)
    story.append(PageBreak())

    # =========================================================================
    # SEÇÃO 2: INTRODUÇÃO E CONTEXTO DO NEGÓCIO (PÁGINA 2)
    # =========================================================================
    story.append(Paragraph("2. Introdução e Contexto de Negócio", styles['H1']))
    story.append(Paragraph(
        "A evasão no ensino superior e o sofrimento psíquico discente constituem desafios estratégicos de primeira ordem para a administração universitária. Sob o paradigma de <b>Business Intelligence (BI) e Inteligência Empresarial aplicada à Gestão Educacional</b>, a instituição atua como decisora central na alocação de recursos públicos e humanos limitados (bolsas de assistência estudantil, serviços de acolhimento psicossocial e organização de calendários acadêmicos). Identificar padrões empíricos associados ao adoecimento mental discente permite transformar dados brutos em decisões informadas e intervenções preventivas estruturadas.",
        styles['Body']
    ))
    story.append(Paragraph(
        "<b>Origem e Rastreabilidade da Base:</b> Os dados decorrem do <i>Student Depression Dataset</i>, originalmente disponibilizado no Kaggle por Shodolamu Opeyemi (<code>hopesb/student-depression-dataset</code>, 27.901 linhas e 18 colunas), sob licença aberta <b>Apache 2.0</b>. Utilizou-se o espelho integral hospedado no Hugging Face Datasets (<code>urmah/student-depression-analysis</code>). Confirmou-se tratar-se da versão volumosa integral, afastando homônimos reduzidos (~500 linhas).",
        styles['Body']
    ))
    story.append(Paragraph(
        "<b>Objetivo Geral e Perguntas Decisórias (P1 a P5):</b> Avaliar a prevalência e a força de associação entre determinantes acadêmicos, comportamentais e socioeconômicos e o indicativo de depressão autorrelatada, subsidiando a Pró-Reitoria de Assistência Estudantil:",
        styles['Body']
    ))
    
    questions_data = [
        [Paragraph("<b>#</b>", styles['TableHeader']), 
         Paragraph("<b>Pergunta de Negócio (BI)</b>", styles['TableHeader']), 
         Paragraph("<b>Variáveis Envolvidas</b>", styles['TableHeader']), 
         Paragraph("<b>Decisão Organizacional / Impacto</b>", styles['TableHeader'])],
        
        [Paragraph("<b>P1</b>", styles['TableTextBold']),
         Paragraph("Qual a proporção estimada de estudantes com indicativo de depressão na população amostrada?", styles['TableText']),
         Paragraph("<code>Depression</code> (0/1)", styles['TableText']),
         Paragraph("Dimensionamento de capacidade e planejamento do núcleo psicossocial.", styles['TableText'])],
        
        [Paragraph("<b>P2</b>", styles['TableTextBold']),
         Paragraph("A sobrecarga curricular percebida difere entre quem tem e quem não tem indicativo de depressão?", styles['TableText']),
         Paragraph("<code>Academic Pressure</code> (0–5) × <code>Depression</code>", styles['TableText']),
         Paragraph("Ajuste pedagógico de matriz curricular e modulação de avaliações.", styles['TableText'])],
        
        [Paragraph("<b>P3</b>", styles['TableTextBold']),
         Paragraph("A duração habitual do sono está associada à ocorrência de indicativo de depressão?", styles['TableText']),
         Paragraph("<code>Sleep Duration</code> (4 faixas) × <code>Depression</code>", styles['TableText']),
         Paragraph("Campanhas preventivas de higiene do sono e ajuste de horários.", styles['TableText'])],
        
        [Paragraph("<b>P4</b>", styles['TableTextBold']),
         Paragraph("A prevalência de depressão varia e exibe tendência linear crescente com o estresse financeiro?", styles['TableText']),
         Paragraph("<code>Financial Stress</code> (1–5) × <code>Depression</code>", styles['TableText']),
         Paragraph("Focalização prioritária de auxílios e bolsas de permanência discente.", styles['TableText'])],
        
        [Paragraph("<b>P5</b>", styles['TableTextBold']),
         Paragraph("Existe correlação substantiva entre satisfação com os estudos e rendimento acadêmico (CGPA)?", styles['TableText']),
         Paragraph("<code>Study Satisfaction</code> (0–5) × <code>CGPA</code> (0–10)", styles['TableText']),
         Paragraph("Desvincular o acolhimento institucional de critérios de notas altas.", styles['TableText'])],
    ]
    t_q = Table(questions_data, colWidths=[20, 190, 140, 172])
    t_q.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_q)
    story.append(Spacer(1, 10))
    story.append(PageBreak())

    # =========================================================================
    # SEÇÃO 3: METODOLOGIA E TRATAMENTO DOS DADOS (PÁGINA 3)
    # =========================================================================
    story.append(Paragraph("3. Metodologia e Tratamento dos Dados", styles['H1']))
    story.append(Paragraph(
        "<b>Ambiente Computacional e Reprodutibilidade:</b> O pipeline foi construído em Python 3.14 (pacotes <code>pandas</code>, <code>numpy</code>, <code>scipy</code>, <code>statsmodels</code>, <code>matplotlib</code>, <code>seaborn</code> e <code>reportlab</code>), consolidado no notebook <code>analise_depressao.ipynb</code> sob semente aleatória fixa (42). Todos os caminhos de dados e saídas são estritamente relativos (<code>data/</code> e <code>outputs/</code>).",
        styles['Body']
    ))
    story.append(Paragraph(
        "<b>Auditoria e Higienização dos Dados (Contabilidade Rigorosa):</b> A base original possuía 27.901 linhas e 18 colunas. O protocolo reprodutível de higienização compreendeu:",
        styles['Body']
    ))
    story.append(Paragraph("• <b>Valores Ausentes:</b> Apenas 3 registros em <code>Financial Stress</code> possuíam valores nulos (IDs 22377, 68910 e 97610; 0,01% da base), excluídos por análise de casos completos sem afetar o equilíbrio amostral.", styles['Bullet']))
    story.append(Paragraph("• <b>Filtragem de Escopo Discente:</b> 31 registros (0,11%) possuíam ocupações não-estudantis (ex.: <i>Civil Engineer, Architect</i>), sendo excluídos para assegurar estrita representatividade estudantil.", styles['Bullet']))
    story.append(Paragraph("• <b>Categorias Espúrias 'Others':</b> Excluíram-se 18 ocorrências em <code>Sleep Duration</code> e 12 em <code>Dietary Habits</code> (30 casos, 0,11%) por ausência de significado discriminatório.", styles['Bullet']))
    story.append(Paragraph("• <b>Descarte de Colunas Constantes:</b> As colunas <code>Work Pressure</code> e <code>Job Satisfaction</code> continham 99,99% e 99,97% de valores zerados (por ausência de vínculo empregatício discente formal), sendo descartadas.", styles['Bullet']))
    story.append(Paragraph("• <b>Tratamento dos Zeros de CGPA e Sensibilidade:</b> Identificaram-se 9 estudantes com CGPA = 0,0 (0,03%), enquanto o percentil 1% é 5,11. Esses registros foram classificados como notas não lançadas/inválidas e removidos das análises de rendimento. A análise de sensibilidade comprovou que a mediana do CGPA permanece estritamente em <b>7,77</b> (IQR = 2,63) com ou sem esses registros, e a média varia apenas 0,003 ponto (7,656 vs. 7,659).", styles['Bullet']))
    story.append(Paragraph("• <b>Tratamento Padronizado dos Zeros em Escalas Likert:</b> Identificaram-se 9 zeros em <code>Academic Pressure</code> (0,03%) e 10 zeros em <code>Study Satisfaction</code> (0,04%). Como essas escalas adotam domínio de 1 a 5 (conforme padronizado em <code>Financial Stress</code>), esses zeros refletem código de não-resposta. Pela análise de sensibilidade, mantê-los na base altera a média em menos de 0,0011 ponto e mantém a mediana idêntica em 3,0.", styles['Bullet']))
    story.append(Paragraph("• <b>Suposições da Amostra (Idades e Horas):</b> A coluna <code>Work/Study Hours</code> possui 1.700 casos com valor 0 (6,09%), o que se cogita decorrer de períodos de férias ou trancamento de matrícula; <i>trata-se de uma possível explicação, não verificável com esta base de dados</i>. Da mesma forma, 12 casos (0,04%) de idade entre 44 e 59 anos foram mantidos como outliers naturais válidos sob a suposição de alunos de pós-graduação ou ingresso tardio; <i>trata-se, igualmente, de uma possível explicação, não verificável com esta base de dados</i>.", styles['Bullet']))
    story.append(Paragraph(
        "<b>Volume Amostral Final Tratado:</b> <b>27.837 estudantes universitários</b> (apenas 64 linhas descartadas no total, correspondendo a meros <b>0,23%</b> do volume original).",
        styles['Body']
    ))
    story.append(Paragraph(
        "<b>Pressupostos e Rigor Metodológico:</b> Em grandes volumes amostrais (<i>N</i> &gt; 27.000), testes de hipóteses de normalidade (Shapiro-Wilk) tornam-se hiper-sensíveis a desvios mínimos. A verificação de pressupostos foi conduzida por <b>inspeção visual de gráficos Q-Q e histogramas</b> (<code>outputs/06_pressupostos_normais.png</code>), confirmando o comportamento em patamares discretos das escalas ordinais e embasando a priorização de métodos não-paramétricos (Mann-Whitney U e correlação de Spearman).",
        styles['Body']
    ))
    
    story.append(PageBreak())

    # =========================================================================
    # SEÇÃO 4: ANÁLISE DESCRITIVA E EXPLORATÓRIA (PÁGINA 3 / 4)
    # =========================================================================
    story.append(Paragraph("4. Análise Descritiva e Exploratória dos Dados", styles['H1']))
    story.append(Paragraph(
        "A análise univariada e bivariada sintetiza o perfil sociodemográfico, comportamental e acadêmico dos 27.837 discentes avaliados.",
        styles['Body']
    ))
    
    # Tabela 1: Descritiva das Numéricas
    story.append(Paragraph("<b>Tabela 1: Estatísticas Descritivas das Variáveis Numéricas e Escalas (N = 27.837)</b>", styles['H2']))
    t1_data = [
        [Paragraph("<b>Variável</b>", styles['TableHeader']),
         Paragraph("<b>Média</b>", styles['TableHeader']),
         Paragraph("<b>Desv. Padrão</b>", styles['TableHeader']),
         Paragraph("<b>Mediana</b>", styles['TableHeader']),
         Paragraph("<b>IQR</b>", styles['TableHeader']),
         Paragraph("<b>Mín.</b>", styles['TableHeader']),
         Paragraph("<b>Máx.</b>", styles['TableHeader']),
         Paragraph("<b>Assimetria</b>", styles['TableHeader']),
         Paragraph("<b>Curtose</b>", styles['TableHeader'])],
        
        [Paragraph("<b>Age</b> (Idade)", styles['TableTextBold']), Paragraph("25,82", styles['TableText']), Paragraph("4,91", styles['TableText']), Paragraph("25,00", styles['TableText']), Paragraph("9,00", styles['TableText']), Paragraph("18,0", styles['TableText']), Paragraph("59,0", styles['TableText']), Paragraph("+0,13", styles['TableText']), Paragraph("-0,85", styles['TableText'])],
        [Paragraph("<b>CGPA</b> (s/ zeros)", styles['TableTextBold']), Paragraph("7,66", styles['TableText']), Paragraph("1,46", styles['TableText']), Paragraph("7,77", styles['TableText']), Paragraph("2,63", styles['TableText']), Paragraph("5,03", styles['TableText']), Paragraph("10,0", styles['TableText']), Paragraph("-0,07", styles['TableText']), Paragraph("-1,23", styles['TableText'])],
        [Paragraph("<b>Academic Pressure</b> (0–5)", styles['TableTextBold']), Paragraph("3,14", styles['TableText']), Paragraph("1,38", styles['TableText']), Paragraph("3,00", styles['TableText']), Paragraph("2,00", styles['TableText']), Paragraph("0,0", styles['TableText']), Paragraph("5,0", styles['TableText']), Paragraph("-0,13", styles['TableText']), Paragraph("-1,16", styles['TableText'])],
        [Paragraph("<b>Study Satisfaction</b> (0–5)", styles['TableTextBold']), Paragraph("2,94", styles['TableText']), Paragraph("1,36", styles['TableText']), Paragraph("3,00", styles['TableText']), Paragraph("2,00", styles['TableText']), Paragraph("0,0", styles['TableText']), Paragraph("5,0", styles['TableText']), Paragraph("+0,01", styles['TableText']), Paragraph("-1,22", styles['TableText'])],
        [Paragraph("<b>Work/Study Hours</b>", styles['TableTextBold']), Paragraph("7,16", styles['TableText']), Paragraph("3,71", styles['TableText']), Paragraph("8,00", styles['TableText']), Paragraph("6,00", styles['TableText']), Paragraph("0,0", styles['TableText']), Paragraph("12,0", styles['TableText']), Paragraph("-0,46", styles['TableText']), Paragraph("-1,00", styles['TableText'])],
        [Paragraph("<b>Financial Stress</b> (1–5)", styles['TableTextBold']), Paragraph("3,14", styles['TableText']), Paragraph("1,44", styles['TableText']), Paragraph("3,00", styles['TableText']), Paragraph("2,00", styles['TableText']), Paragraph("1,0", styles['TableText']), Paragraph("5,0", styles['TableText']), Paragraph("-0,13", styles['TableText']), Paragraph("-1,32", styles['TableText'])],
    ]
    t1 = Table(t1_data, colWidths=[110, 48, 55, 48, 45, 38, 38, 55, 55])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t1)
    story.append(Spacer(1, 6))

    # Tabela 2: Frequências das Categóricas
    story.append(Paragraph("<b>Tabela 2: Distribuição de Frequências das Variáveis Categóricas (N = 27.837)</b>", styles['H2']))
    t2_data = [
        [Paragraph("<b>Variável</b>", styles['TableHeader']), Paragraph("<b>Categorias e Níveis</b>", styles['TableHeader']), Paragraph("<b>Freq. Absoluta (N)</b>", styles['TableHeader']), Paragraph("<b>Freq. Relativa (%)</b>", styles['TableHeader'])],
        [Paragraph("<b>Depression (Desfecho)</b>", styles['TableTextBold']), Paragraph("1 (Com indicativo) / 0 (Sem indicativo)", styles['TableText']), Paragraph("16.290 / 11.547", styles['TableText']), Paragraph("<b>58,52%</b> / 41,48%", styles['TableText'])],
        [Paragraph("<b>Gender (Gênero)</b>", styles['TableTextBold']), Paragraph("Masculino ('Male') / Feminino ('Female')", styles['TableText']), Paragraph("15.511 / 12.326", styles['TableText']), Paragraph("55,72% / 44,28%", styles['TableText'])],
        [Paragraph("<b>Sleep Duration (Sono)</b>", styles['TableTextBold']), Paragraph("&lt; 5h / 7–8h / 5–6h / &gt; 8h", styles['TableText']), Paragraph("8.297 / 7.334 / 6.172 / 6.034", styles['TableText']), Paragraph("29,81% / 26,35% / 22,17% / 21,68%", styles['TableText'])],
        [Paragraph("<b>Dietary Habits (Dieta)</b>", styles['TableTextBold']), Paragraph("Unhealthy / Moderate / Healthy", styles['TableText']), Paragraph("10.300 / 9.903 / 7.634", styles['TableText']), Paragraph("37,00% / 35,57% / 27,42%", styles['TableText'])],
        [Paragraph("<b>Suicidal Thoughts</b>", styles['TableTextBold']), Paragraph("Sim ('Yes') / Não ('No')", styles['TableText']), Paragraph("17.610 / 10.227", styles['TableText']), Paragraph("<b>63,26%</b> / 36,74%", styles['TableText'])],
        [Paragraph("<b>Family History</b>", styles['TableTextBold']), Paragraph("Não ('No') / Sim ('Yes')", styles['TableText']), Paragraph("14.364 / 13.473", styles['TableText']), Paragraph("51,60% / 48,40%", styles['TableText'])],
    ]
    t2 = Table(t2_data, colWidths=[120, 210, 100, 92])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), secondary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t2)
    story.append(Spacer(1, 6))

    # Inclusão da Figura 1 (Distribuições Numéricas)
    if os.path.exists("outputs/01_distribuicoes_numericas.png"):
        img1 = Image("outputs/01_distribuicoes_numericas.png", width=490, height=195)
        story.append(img1)
        story.append(Paragraph("<b>Figura 1:</b> Distribuições empíricas e curvas KDE das 6 variáveis numéricas e escalas discentes.", styles['Caption']))
    
    story.append(PageBreak())

    # Continuação da Seção 4 (Página 4)
    story.append(Paragraph("<b>Comportamento Bivariado: Sono e Estresse Financeiro vs. Depressão</b>", styles['H2']))
    story.append(Paragraph(
        "A Tabela 3 detalha a taxa de depressão estratificada pelas faixas de sono (P3) e pelos níveis de estresse financeiro (P4). Nota-se que o estresse financeiro exibe um gradiente monotônico estrito, enquanto o sono revela maior prevalência nos extremos de privação severa (&lt; 5 horas).",
        styles['Body']
    ))

    t3_data = [
        [Paragraph("<b>Duração do Sono</b>", styles['TableHeader']), Paragraph("<b>Taxa Depressão (%)</b>", styles['TableHeader']), Paragraph("<b>Nível Estresse Financeiro</b>", styles['TableHeader']), Paragraph("<b>Taxa Depressão (%)</b>", styles['TableHeader'])],
        [Paragraph("&lt; 5 hours (Privação severa)", styles['TableText']), Paragraph("<b>64,51%</b> (5.352 / 8.297)", styles['TableTextBold']), Paragraph("Nível 1 (Mínimo estresse)", styles['TableText']), Paragraph("<b>31,81%</b> (1.625 / 5.108)", styles['TableTextBold'])],
        [Paragraph("5–6 hours (Sono curto)", styles['TableText']), Paragraph("<b>56,85%</b> (3.509 / 6.172)", styles['TableTextBold']), Paragraph("Nível 2 (Baixo estresse)", styles['TableText']), Paragraph("<b>42,94%</b> (2.170 / 5.053)", styles['TableTextBold'])],
        [Paragraph("7–8 hours (Sono padrão)", styles['TableText']), Paragraph("<b>59,45%</b> (4.360 / 7.334)", styles['TableTextBold']), Paragraph("Nível 3 (Estresse moderado)", styles['TableText']), Paragraph("<b>58,91%</b> (3.071 / 5.213)", styles['TableTextBold'])],
        [Paragraph("&gt; 8 hours (Sono prolongado)", styles['TableText']), Paragraph("<b>50,86%</b> (3.069 / 6.034)", styles['TableTextBold']), Paragraph("Nível 4 (Alto estresse)", styles['TableText']), Paragraph("<b>69,09%</b> (3.983 / 5.765)", styles['TableTextBold'])],
        [Paragraph("<b>Média Global da Amostra</b>", styles['TableTextBold']), Paragraph("<b>58,52%</b> (16.290 / 27.837)", styles['TableTextBold']), Paragraph("Nível 5 (Máximo estresse)", styles['TableText']), Paragraph("<b>81,23%</b> (5.441 / 6.698)", styles['TableTextBold'])],
    ]
    t3 = Table(t3_data, colWidths=[150, 111, 150, 111])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t3)
    story.append(Spacer(1, 6))

    # Inclusão de Imagens lado a lado (Sono e Pressão Acadêmica)
    if os.path.exists("outputs/02_sleep_vs_depression.png") and os.path.exists("outputs/03_academic_pressure_by_depression.png"):
        img_sleep = Image("outputs/02_sleep_vs_depression.png", width=255, height=145)
        img_ap = Image("outputs/03_academic_pressure_by_depression.png", width=255, height=145)
        fig_table = Table([[img_sleep, img_ap]], colWidths=[261, 261])
        fig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(fig_table)
        story.append(Paragraph("<b>Figura 2:</b> Proporção de depressão por faixa de sono (esquerda) e distribuição da pressão acadêmica por status de depressão (direita).", styles['Caption']))

    # Inclusão da Matriz de Correlação
    if os.path.exists("outputs/05_correlation_matrices.png"):
        img_corr = Image("outputs/05_correlation_matrices.png", width=490, height=150)
        story.append(img_corr)
        story.append(Paragraph("<b>Figura 3:</b> Mapas de calor das matrizes de correlação linear de Pearson (esquerda) e monotônica de Spearman (direita).", styles['Caption']))

    story.append(PageBreak())

    # =========================================================================
    # SEÇÃO 5: ANÁLISE INFERENCIAL E VALIDAÇÃO DE HIPÓTESES (PÁGINA 5 / 6)
    # =========================================================================
    story.append(Paragraph("5. Análise Inferencial e Validação de Hipóteses", styles['H1']))
    story.append(Paragraph(
        "Declarou-se o nível de significância prévio α = 0,05. Cada teste foi vinculado às hipóteses formais de pesquisa (H₀ e H₁), acompanhado de sua estatística, graus de liberdade, p-valor e <b>tamanho de efeito padronizado</b>.",
        styles['Body']
    ))

    t_inf_data = [
        [Paragraph("<b>#</b>", styles['TableHeader']),
         Paragraph("<b>Hipóteses Formais (H₀ e H₁)</b>", styles['TableHeader']),
         Paragraph("<b>Procedimento</b>", styles['TableHeader']),
         Paragraph("<b>Estatística & p-valor</b>", styles['TableHeader']),
         Paragraph("<b>Tamanho de Efeito</b>", styles['TableHeader']),
         Paragraph("<b>Decisão (α = 0,05)</b>", styles['TableHeader'])],
        
        [Paragraph("<b>P1</b>", styles['TableTextBold']),
         Paragraph("Estimar proporção populacional (<i>p</i>) de depressão na população amostrada.", styles['TableText']),
         Paragraph("IC 95% de Wilson score", styles['TableText']),
         Paragraph("<i>k</i> = 16.290, <i>N</i> = 27.837<br/>p̂ = <b>58,52%</b>", styles['TableText']),
         Paragraph("Margem: <b>±0,58%</b><br/><b>[57,94%, 59,10%]</b>", styles['TableTextBold']),
         Paragraph("Estimativa precisa para a população da pesquisa.", styles['TableText'])],
        
        [Paragraph("<b>P2</b>", styles['TableTextBold']),
         Paragraph("<b>H₀:</b> <i>F</i><sub>com</sub>(<i>x</i>) = <i>F</i><sub>sem</sub>(<i>x</i>)<br/><b>H₁:</b> <i>F</i><sub>com</sub>(<i>x</i>) ≠ <i>F</i><sub>sem</sub>(<i>x</i>)", styles['TableText']),
         Paragraph("<b>Mann-Whitney U</b> (Principal)<br/>+ Welch <i>t</i> (Confirmatório)", styles['TableText']),
         Paragraph("<i>U</i> = 1,45 × 10<sup>8</sup>, <i>p</i> &lt; 0,0001<br/><i>t</i> = 89,21, <i>p</i> &lt; 0,0001", styles['TableText']),
         Paragraph("<i>r<sub>rb</sub></i> = <b>0,5408</b><br/>Prob. Superioridade: <b>≈ 77%</b> (empates/2)<br/><i>d</i> de Cohen = <b>1,0950</b>", styles['TableTextBold']),
         Paragraph("<b>Rejeita H₀</b>.<br/>Associação de grande magnitude.", styles['TableTextBold'])],
        
        [Paragraph("<b>P3</b>", styles['TableTextBold']),
         Paragraph("<b>H₀:</b> Duração do sono e depressão são independentes.<br/><b>H₁:</b> Sono e depressão estão associados.", styles['TableText']),
         Paragraph("Qui-Quadrado de Independência (χ²)", styles['TableText']),
         Paragraph("χ² = 277,90, <i>gl</i> = 3<br/><i>p</i> = 6,03 × 10<sup>-60</sup>", styles['TableText']),
         Paragraph("Cramér's <i>V</i> = <b>0,0999 (~0,10)</b><br/>(Efeito Fraco, não-monotônico)", styles['TableText']),
         Paragraph("<b>Rejeita H₀</b>.<br/>Relevância prática modesta.", styles['TableText'])],
        
        [Paragraph("<b>P4</b>", styles['TableTextBold']),
         Paragraph("<b>H₀:</b> Independência e sem tendência.<br/><b>H₁:</b> Tendência monotônica crescente de depressão com estresse financeiro.", styles['TableText']),
         Paragraph("Qui-Quadrado (χ²)<br/>+ Tendência de <b>Cochran-Armitage</b>", styles['TableText']),
         Paragraph("χ² = 3.695,04, <i>gl</i> = 4, <i>p</i> &lt; 0,0001<br/><i>Z</i> = <b>60,67</b>, <i>p</i> &lt; 0,0001", styles['TableText']),
         Paragraph("Cramér's <i>V</i> = <b>0,3643</b> (<b>Moderado</b>)<br/>Tendência monotônica <b>Forte</b> (31,8% a 81,2%)", styles['TableTextBold']),
         Paragraph("<b>Rejeita H₀</b>.<br/>Forte gradiente socioeconômico.", styles['TableTextBold'])],
        
        [Paragraph("<b>P5</b>", styles['TableTextBold']),
         Paragraph("<b>H₀:</b> Correlação nula (ρ = 0).<br/><b>H₁:</b> Correlação diferente de zero (ρ ≠ 0).", styles['TableText']),
         Paragraph("Correlação Monotônica de <b>Spearman (ρ)</b><br/>+ Pearson (<i>r</i>)", styles['TableText']),
         Paragraph("<i>N</i> = 27.828<br/><i>p</i> = 6,85 × 10<sup>-15</sup>", styles['TableText']),
         Paragraph("Spearman <i>ρ</i> = <b>-0,0467</b><br/>Pearson <i>r</i> = <b>-0,0466</b>", styles['TableTextBold']),
         Paragraph("<b>Rejeita H₀</b> matemático (poder do <i>N</i>), mas <b>EFEITO PRÁTICO DESPREZÍVEL</b> (|ρ| &lt; 0,10).", styles['TableTextBold'])],
    ]
    t_inf = Table(t_inf_data, colWidths=[20, 130, 95, 87, 105, 85])
    t_inf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_inf)
    story.append(Spacer(1, 6))

    # Inclusão do Gráfico de Dispersão (Item 1 do roteiro)
    if os.path.exists("outputs/04_dispersao_satisfacao_cgpa.png"):
        img_scatter = Image("outputs/04_dispersao_satisfacao_cgpa.png", width=460, height=215)
        story.append(img_scatter)
        story.append(Paragraph("<b>Figura 4:</b> Gráfico de dispersão entre Satisfação com os Estudos (0–5) e Rendimento Acadêmico Acumulado (CGPA: 0–10), com jitter horizontal (±0,15), transparência de densidade, reta de tendência linear e indicação do coeficiente de correlação de postos de Spearman (ρ = -0,0467, p &lt; 0,001).", styles['Caption']))

    story.append(PageBreak())

    # Continuação da Seção 5 (Página 6): Interpretação e Multiplicidade
    story.append(Paragraph(
        "<b>Interpretação Substantiva dos Efeitos:</b><br/>"
        "1. <b>Probabilidade de Superioridade (P2):</b> A correlação bisserial por postos de <i>r<sub>rb</sub></i> = 0,5408 converte-se em uma <b>probabilidade de superioridade de aproximadamente 77%, contando empates pela metade</b> (<i>CLES</i> = (<i>r<sub>rb</sub></i> + 1) / 2). Esse refinamento conceitual é metodologicamente necessário em virtude da natureza discreta da escala ordinal de pressão acadêmica (0 a 5), na qual há um número substantivo de empates entre pares de estudantes.<br/>"
        "2. <b>Gradiente Financeiro vs. Sono (P4 vs. P3):</b> O estresse financeiro exibe um <i>V</i> de Cramér de <b>0,36 (moderado)</b> associado a uma tendência monotônica <b>forte</b> comprovada pelo teste de Cochran-Armitage (<i>Z</i> = 60,67), saltando de 31,8% no nível 1 para 81,2% no nível 5. Em contrapartida, o sono exibe associação global fraca (<i>V</i> = 0,10) e comportamento não-monotônico, indicando que a assistência financeira possui impacto associativo preponderante.<br/>"
        "3. <b>Dispersão e Desconexão Prática (P5):</b> Como ilustrado na <b>Figura 4</b>, a dispersão uniforme com jitter horizontal e a inclinação praticamente plana da linha de tendência linear evidenciam que o coeficiente de Spearman (<i>ρ</i> = -0,0467; <i>p</i> &lt; 0,0001), embora formalmente significativo pelo tamanho amostral expressivo (<i>N</i> = 27.828), possui relevância prática negligenciável (|<i>ρ</i>| &lt; 0,10).<br/>"
        "4. <b>Controle de Comparações Múltiplas:</b> O estudo compreende <b>4 famílias de hipóteses</b> (a P1 é um intervalo de confiança de estimativa, e a P2 envolve dois testes concorrentes sobre a mesma hipótese). Aplicando a correção sequencial de Holm-Bonferroni sobre as 4 famílias (<i>p</i><sub>1</sub>, <i>p</i><sub>2</sub>, <i>p</i><sub>3</sub>, <i>p</i><sub>4</sub> &lt; 10<sup>-14</sup>), todas as hipóteses nulas permanecem rejeitadas com folga, assegurando controle estrito da taxa de erro global (FWER ≤ 0,05).",
        styles['Body']
    ))
    story.append(Spacer(1, 6))

    # =========================================================================
    # SEÇÃO 6: RECOMENDAÇÕES PRÁTICAS E PLANO DE AÇÃO DE BI (PÁGINA 6)
    # =========================================================================
    story.append(Paragraph("6. Recomendações Práticas e Plano de Ação de BI", styles['H1']))
    story.append(Paragraph(
        "Apoiado nas evidências estatísticas, propõe-se um plano de ação para a gestão universitária (Pró-Reitorias de Assistência Estudantil e de Graduação):",
        styles['Body']
    ))

    recs_data = [
        [Paragraph("<b>Eixo Estratégico</b>", styles['TableHeader']), Paragraph("<b>Evidência Empírica Base</b>", styles['TableHeader']), Paragraph("<b>Ação Recomendada (Plano Institucional de BI)</b>", styles['TableHeader'])],
        
        [Paragraph("<b>1. Permanência e Assistência Material</b>", styles['TableTextBold']),
         Paragraph("P4: 81,2% de depressão no nível 5 de estresse financeiro vs. 31,8% no nível 1 (Cochran-Armitage <i>Z</i> = 60,67).", styles['TableText']),
         Paragraph("<b>Priorização focalizada do PNAES/Bolsas:</b> Utilizar questionário socioeconômico semestral para identificar ativamente discentes nos níveis 4 e 5 de vulnerabilidade, canalizando bolsas de permanência, moradia e alimentação prioritária antes da ocorrência de evasão.", styles['TableText'])],
        
        [Paragraph("<b>2. Gestão Curricular e Pedagógica</b>", styles['TableTextBold']),
         Paragraph("P2: <i>d</i> de Cohen = 1,10; probabilidade de superioridade de aproximadamente 77%, contando empates pela metade, na pressão acadêmica.", styles['TableText']),
         Paragraph("<b>Escalonamento e Modulação de Avaliações:</b> Implementar diretrizes pedagógicas para que colegiados de curso evitem concentração excessiva de entregas e provas na mesma semana, criando fóruns de apoio psicopedagógico em disciplinas sobrecarregadas.", styles['TableText'])],
        
        [Paragraph("<b>3. Higiene do Sono e Rotina</b>", styles['TableTextBold']),
         Paragraph("P3: Maior taxa de depressão concentrada na privação extrema (&lt; 5h = 64,51%).", styles['TableText']),
         Paragraph("<b>Oficinas de Manejo de Rotina e Gestão de Turnos:</b> Promover oficinas de saúde preventiva do sono durante o acolhimento institucional e avaliar flexibilizações de horários para cursos com aulas em turnos extremos.", styles['TableText'])],
        
        [Paragraph("<b>4. Política de Acolhimento Sem Viés de Nota</b>", styles['TableTextBold']),
         Paragraph("P5: Correlação insignificante entre rendimento (CGPA) e satisfação (<i>ρ</i> = -0,047; Figura 4).", styles['TableText']),
         Paragraph("<b>Desvinculação entre Suporte Psicológico e Coeficiente de Rendimento:</b> O serviço psicopedagógico não deve condicionar nem priorizar atendimentos com base em notas baixas, visto que alunos com CGPA de excelência sofrem igualmente de sobrecarga e sofrimento psíquico.", styles['TableText'])],
    ]
    t_rec = Table(recs_data, colWidths=[120, 150, 252])
    t_rec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), secondary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_rec)

    story.append(PageBreak())

    # =========================================================================
    # SEÇÃO 7: REFERÊNCIAS, APÊNDICES E LIMITAÇÕES (PÁGINA 7)
    # =========================================================================
    story.append(Paragraph("7. Referências, Apêndices e Limitações Metodológicas", styles['H1']))
    
    # Caixa Evidente de Repositório do GitHub (Item 6)
    gh_box_data = [
        [Paragraph("<b>LINK DO REPOSITÓRIO PÚBLICO (GITHUB) & FONTES:</b>", styles['GithubPlaceholder'])],
        [Paragraph(
            "• <b>Repositório do Projeto:</b> <code>https://github.com/brunomartinsgg/sisb110-depressao-estudantes</code><br/>"
            "• <b>Fonte Primária Original:</b> <i>Student Depression Dataset</i> no Kaggle (<code>https://www.kaggle.com/datasets/hopesb/student-depression-dataset</code>, autor Shodolamu Opeyemi, Licença Apache 2.0).<br/>"
            "• <b>Espelho Utilizado:</b> Hugging Face Datasets (<code>https://huggingface.co/datasets/urmah/student-depression-analysis</code>).",
            styles['CalloutText']
        )]
    ]
    t_gh = Table(gh_box_data, colWidths=[522])
    t_gh.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), warning_bg),
        ('BOX', (0, 0), (-1, -1), 1, warning_border),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_gh)
    story.append(Spacer(1, 6))

    # Tabela de Tipagem Completa (Apêndice)
    story.append(Paragraph("<b>Apêndice Metodológico: Dicionário de Dados e Tipagem das Variáveis</b>", styles['H2']))
    t_types_data = [
        [Paragraph("<b>Coluna</b>", styles['TableHeader']), Paragraph("<b>Classificação Estatística</b>", styles['TableHeader']), Paragraph("<b>Domínio / Unidade</b>", styles['TableHeader']), Paragraph("<b>Tratamento e Decisão Metodológica</b>", styles['TableHeader'])],
        [Paragraph("<code>id</code>", styles['TableTextBold']), Paragraph("Identificador Técnico", styles['TableText']), Paragraph("Inteiro único", styles['TableText']), Paragraph("Mantido para rastreabilidade; 0 duplicatas.", styles['TableText'])],
        [Paragraph("<code>Gender</code>", styles['TableTextBold']), Paragraph("Categórica Nominal", styles['TableText']), Paragraph("'Male', 'Female'", styles['TableText']), Paragraph("Tipada como categoria dicotômica.", styles['TableText'])],
        [Paragraph("<code>Age</code>", styles['TableTextBold']), Paragraph("<b>Quantitativa Discreta</b>", styles['TableTextBold']), Paragraph("18 a 59 anos inteiros", styles['TableText']), Paragraph("Mantidos outliers de Tukey (&gt;43,5 anos) sob suposição discente.", styles['TableText'])],
        [Paragraph("<code>City</code>", styles['TableTextBold']), Paragraph("Categórica Nominal", styles['TableText']), Paragraph("52 municípios", styles['TableText']), Paragraph("Mantida para caracterização geográfica.", styles['TableText'])],
        [Paragraph("<code>Profession</code>", styles['TableTextBold']), Paragraph("Categórica Nominal", styles['TableText']), Paragraph("'Student' (exclusivo)", styles['TableText']), Paragraph("Filtrada; 31 registros não-estudantes removidos.", styles['TableText'])],
        [Paragraph("<code>Academic Pressure</code>", styles['TableTextBold']), Paragraph("Qualitativa Ordinal / Escala", styles['TableText']), Paragraph("0 a 5 (escala)", styles['TableText']), Paragraph("9 zeros analisados por sensibilidade e mantidos.", styles['TableText'])],
        [Paragraph("<code>CGPA</code>", styles['TableTextBold']), Paragraph("Quantitativa Contínua/Razão", styles['TableText']), Paragraph("0,0 a 10,0", styles['TableText']), Paragraph("9 zeros tratados como ausentes para análises de CGPA.", styles['TableText'])],
        [Paragraph("<code>Study Satisfaction</code>", styles['TableTextBold']), Paragraph("Qualitativa Ordinal / Escala", styles['TableText']), Paragraph("0 a 5 (escala)", styles['TableText']), Paragraph("10 zeros analisados por sensibilidade e mantidos.", styles['TableText'])],
        [Paragraph("<code>Sleep Duration</code>", styles['TableTextBold']), Paragraph("Categórica Ordinal", styles['TableText']), Paragraph("4 faixas de horas", styles['TableText']), Paragraph("18 registros 'Others' descartados por ruído.", styles['TableText'])],
        [Paragraph("<code>Dietary Habits</code>", styles['TableTextBold']), Paragraph("Categórica Ordinal", styles['TableText']), Paragraph("3 níveis qualitativos", styles['TableText']), Paragraph("12 registros 'Others' descartados por ruído.", styles['TableText'])],
        [Paragraph("<code>Degree</code>", styles['TableTextBold']), Paragraph("Categórica Nominal", styles['TableText']), Paragraph("28 títulos acadêmicos", styles['TableText']), Paragraph("Mantida para contextualização do grau acadêmico.", styles['TableText'])],
        [Paragraph("<code>Suicidal Thoughts</code>", styles['TableTextBold']), Paragraph("Categórica Nominal / Binária", styles['TableText']), Paragraph("'Yes', 'No'", styles['TableText']), Paragraph("Indicador sensível de alerta ético institucional.", styles['TableText'])],
        [Paragraph("<code>Work/Study Hours</code>", styles['TableTextBold']), Paragraph("<b>Quantitativa Discreta</b>", styles['TableTextBold']), Paragraph("0 a 12 horas inteiras/dia", styles['TableText']), Paragraph("6,09% com 0h mantidos sob suposição de férias/trancamento.", styles['TableText'])],
        [Paragraph("<code>Financial Stress</code>", styles['TableTextBold']), Paragraph("Qualitativa Ordinal / Escala", styles['TableText']), Paragraph("1 a 5 (escala)", styles['TableText']), Paragraph("3 nulos pontuais excluídos por complete case analysis.", styles['TableText'])],
        [Paragraph("<code>Family History</code>", styles['TableTextBold']), Paragraph("Categórica Nominal / Binária", styles['TableText']), Paragraph("'Yes', 'No'", styles['TableText']), Paragraph("Histórico familiar de saúde mental autorreportado.", styles['TableText'])],
        [Paragraph("<code>Depression</code>", styles['TableTextBold']), Paragraph("Categórica Nominal / Binária", styles['TableText']), Paragraph("0 (Não), 1 (Sim)", styles['TableText']), Paragraph("<b>Desfecho binário principal de interesse analítico.</b>", styles['TableTextBold'])],
    ]
    t_types = Table(t_types_data, colWidths=[95, 110, 110, 207])
    t_types.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.8),
    ]))
    story.append(t_types)
    story.append(Spacer(1, 6))

    # Limitações e Cuidado Ético
    story.append(Paragraph(
        "<b>Limitações Metodológicas Obrigatórias e Rigor de Interpretação:</b><br/>"
        "1. <b>Natureza Observacional e Causalidade Reversa:</b> Trata-se de um estudo seccional observacional. Toda associação estatística observada não configura relação de causalidade. É altamente plausível a ocorrência de causalidade reversa, na qual discentes que já vivenciam quadros depressivos desenvolvam maior vulnerabilidade financeira subjetiva e percepção amplificada de sobrecarga acadêmica.<br/>"
        "2. <b>Autorrelato vs. Diagnóstico Clínico Estruturado:</b> A mensuração de depressão baseia-se em questionário autoaplicado de percepção individual, carecendo de confirmação diagnóstica via entrevistas psiquiátricas ou instrumentos clínicos validados baseados nos manuais DSM-5 ou CID-11.<br/>"
        "3. <b>Viés de Resposta e Amostra Não Probabilística:</b> As taxas registradas na amostra (58,5% de indicativo de depressão e 63,3% de ideação suicida) são substancialmente superiores às médias epidemiológicas globais em populações gerais de universitários, o que evidencia forte viés de autosseleção na adesão à pesquisa. Os resultados aplicam-se estritamente à população discente representada pelos respondentes deste questionário.<br/>"
        "4. <b>Cuidado Ético Humanizado em Saúde Mental:</b> Os dados relativos a ideação suicida e sofrimento mental exigem tratamento estritamente técnico e confidencial. Devem servir exclusivamente como embasamento para a criação de redes acolhedoras de suporte multiprofissional (psicólogos, assistentes sociais e pedagogos) e nunca para triagens punitivas, vigilância discriminatória ou estigmatização de discentes.",
        styles['Body']
    ))

    # Compilação do PDF com NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Relatório executivo '{pdf_filename}' gerado com sucesso!")

if __name__ == "__main__":
    build_pdf()
