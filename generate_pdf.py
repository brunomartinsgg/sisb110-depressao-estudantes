import os
import sys
import matplotlib
import pandas as pd
import numpy as np
import pymupdf

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
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
# Canvas Customizado para Numeração ABNT (Canto Superior Direito)
# -------------------------------------------------------------------------
class ABNTCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(ABNTCanvas, self).__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        # ABNT: Capa (1), Folha de Rosto (2), Sumário (3), Resumo (4).
        # A numeração visível começa a partir da primeira folha textual (página 5).
        for page_dict in self.pages:
            self.__dict__.update(page_dict)
            page_num = self._pageNumber
            if page_num >= 5:
                self.saveState()
                self.setFont("DejaVuSans", 10)
                self.setFillColor(colors.HexColor("#000000"))
                # Canto superior direito: 2 cm da borda direita (595.3 - 56.7 = 538.6), 2 cm do topo (841.9 - 56.7 = 785.2)
                self.drawRightString(538.6, 792.0, str(page_num))
                self.restoreState()
            super(ABNTCanvas, self).showPage()
        super(ABNTCanvas, self).save()


def build_pdf_flowables(toc_page_numbers=None):
    if toc_page_numbers is None:
        toc_page_numbers = {}

    # Largura útil da mancha gráfica: 595.28 - (85.04 + 56.69) = 453.55 pt
    USABLE_W = 453.5

    # -------------------------------------------------------------------------
    # Estilos Tipográficos ABNT / UFAL
    # -------------------------------------------------------------------------
    base_styles = getSampleStyleSheet()

    styles = {
        'CoverHeader': ParagraphStyle(
            'CoverHeader',
            fontName='DejaVuSans',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#000000'),
            alignment=TA_CENTER,
            spaceAfter=3
        ),
        'CoverAuthor': ParagraphStyle(
            'CoverAuthor',
            fontName='DejaVuSans',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#000000'),
            alignment=TA_CENTER
        ),
        'CoverTitle': ParagraphStyle(
            'CoverTitle',
            fontName='DejaVuSans-Bold',
            fontSize=12,
            leading=17,
            textColor=colors.HexColor('#000000'),
            alignment=TA_CENTER
        ),
        'CoverFooter': ParagraphStyle(
            'CoverFooter',
            fontName='DejaVuSans',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#000000'),
            alignment=TA_CENTER
        ),
        'NotaApresentacao': ParagraphStyle(
            'NotaApresentacao',
            fontName='DejaVuSans',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#000000'),
            alignment=TA_JUSTIFY
        ),
        'HeadingCenter': ParagraphStyle(
            'HeadingCenter',
            fontName='DejaVuSans-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#000000'),
            alignment=TA_CENTER,
            spaceAfter=12
        ),
        'Heading1': ParagraphStyle(
            'Heading1',
            fontName='DejaVuSans-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#000000'),
            alignment=TA_LEFT,
            spaceBefore=16,
            spaceAfter=8,
            keepWithNext=True
        ),
        'Heading2': ParagraphStyle(
            'Heading2',
            fontName='DejaVuSans-Bold',
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#000000'),
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True
        ),
        'Heading3': ParagraphStyle(
            'Heading3',
            fontName='DejaVuSans-Bold',
            fontSize=12,
            leading=15,
            textColor=colors.HexColor('#000000'),
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True
        ),
        'Body': ParagraphStyle(
            'Body',
            fontName='DejaVuSans',
            fontSize=12,
            leading=18,
            textColor=colors.HexColor('#000000'),
            alignment=TA_JUSTIFY,
            firstLineIndent=35.43,  # 1.25 cm
            spaceAfter=4
        ),
        'BodyNoIndent': ParagraphStyle(
            'BodyNoIndent',
            fontName='DejaVuSans',
            fontSize=12,
            leading=18,
            textColor=colors.HexColor('#000000'),
            alignment=TA_JUSTIFY,
            spaceAfter=4
        ),
        'CaptionAbove': ParagraphStyle(
            'CaptionAbove',
            fontName='DejaVuSans-Bold',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#000000'),
            alignment=TA_CENTER,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True
        ),
        'SourceBelow': ParagraphStyle(
            'SourceBelow',
            fontName='DejaVuSans',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#000000'),
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=12
        ),
        'TableCell': ParagraphStyle(
            'TableCell',
            fontName='DejaVuSans',
            fontSize=9,
            leading=11,
            textColor=colors.HexColor('#000000'),
            alignment=TA_CENTER
        ),
        'TableCellLeft': ParagraphStyle(
            'TableCellLeft',
            fontName='DejaVuSans',
            fontSize=9,
            leading=11,
            textColor=colors.HexColor('#000000'),
            alignment=TA_LEFT
        ),
        'TableCellBold': ParagraphStyle(
            'TableCellBold',
            fontName='DejaVuSans-Bold',
            fontSize=9,
            leading=11,
            textColor=colors.HexColor('#000000'),
            alignment=TA_CENTER
        ),
        'RefEntry': ParagraphStyle(
            'RefEntry',
            fontName='DejaVuSans',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#000000'),
            alignment=TA_LEFT,
            spaceAfter=8
        ),
        'TOCItem': ParagraphStyle(
            'TOCItem',
            fontName='DejaVuSans',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#000000'),
            alignment=TA_LEFT
        ),
        'TOCItemBold': ParagraphStyle(
            'TOCItemBold',
            fontName='DejaVuSans-Bold',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#000000'),
            alignment=TA_LEFT
        ),
        'TOCPage': ParagraphStyle(
            'TOCPage',
            fontName='DejaVuSans',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#000000'),
            alignment=TA_RIGHT
        ),
        'TOCPageBold': ParagraphStyle(
            'TOCPageBold',
            fontName='DejaVuSans-Bold',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#000000'),
            alignment=TA_RIGHT
        ),
        # Estilos compactos para o Resumo Executivo (1 página exata)
        'ResumoTitle': ParagraphStyle(
            'ResumoTitle',
            fontName='DejaVuSans-Bold',
            fontSize=12,
            leading=15,
            textColor=colors.HexColor('#000000'),
            alignment=TA_CENTER,
            spaceAfter=4
        ),
        'ResumoSection': ParagraphStyle(
            'ResumoSection',
            fontName='DejaVuSans-Bold',
            fontSize=9.5,
            leading=12.5,
            textColor=colors.HexColor('#1A365D'),
            alignment=TA_LEFT,
            spaceBefore=4,
            spaceAfter=2,
            keepWithNext=True
        ),
        'ResumoBody': ParagraphStyle(
            'ResumoBody',
            fontName='DejaVuSans',
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor('#000000'),
            alignment=TA_JUSTIFY,
            spaceAfter=2
        ),
        'ResumoBullet': ParagraphStyle(
            'ResumoBullet',
            fontName='DejaVuSans',
            fontSize=8.5,
            leading=11.2,
            textColor=colors.HexColor('#000000'),
            alignment=TA_JUSTIFY,
            leftIndent=10,
            spaceAfter=1.5
        ),
        'BulletBody': ParagraphStyle(
            'BulletBody',
            fontName='DejaVuSans',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#000000'),
            alignment=TA_LEFT,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=4
        )
    }

    flowables = []

    # =========================================================================
    # FOLHA 1: CAPA
    # =========================================================================
    flowables.append(Spacer(1, 10))
    flowables.append(Paragraph("UNIVERSIDADE FEDERAL DE ALAGOAS", styles['CoverHeader']))
    flowables.append(Paragraph("CAMPUS ARAPIRACA", styles['CoverHeader']))
    flowables.append(Paragraph("UNIDADE EDUCACIONAL PENEDO", styles['CoverHeader']))
    flowables.append(Paragraph("CURSO BACHARELADO EM SISTEMAS DE INFORMAÇÃO", styles['CoverHeader']))

    flowables.append(Spacer(1, 110))
    flowables.append(Paragraph("BRUNO MARTINS GOMES", styles['CoverAuthor']))

    flowables.append(Spacer(1, 150))
    flowables.append(Paragraph("RELATÓRIO EXECUTIVO DE BUSINESS INTELLIGENCE:", styles['CoverTitle']))
    flowables.append(Spacer(1, 6))
    flowables.append(Paragraph("Análise Estatística e Fatores Associados à Saúde Mental em Estudantes Universitários", styles['CoverTitle']))

    flowables.append(Spacer(1, 180))
    flowables.append(Paragraph("PENEDO - AL", styles['CoverFooter']))
    flowables.append(Paragraph("2026", styles['CoverFooter']))
    flowables.append(PageBreak())

    # =========================================================================
    # FOLHA 2: FOLHA DE ROSTO
    # =========================================================================
    flowables.append(Spacer(1, 15))
    flowables.append(Paragraph("BRUNO MARTINS GOMES", styles['CoverAuthor']))

    flowables.append(Spacer(1, 130))
    flowables.append(Paragraph("RELATÓRIO EXECUTIVO DE BUSINESS INTELLIGENCE:", styles['CoverTitle']))
    flowables.append(Spacer(1, 6))
    flowables.append(Paragraph("Análise Estatística e Fatores Associados à Saúde Mental em Estudantes Universitários", styles['CoverTitle']))

    flowables.append(Spacer(1, 90))
    nota_texto = (
        "Trabalho acadêmico apresentado como requisito de avaliação "
        "na disciplina SISB110 — Ciência dos Dados e Inteligência Empresarial, "
        "do Curso de Bacharelado em Sistemas de Informação da Universidade "
        "Federal de Alagoas, Campus Arapiraca - Unidade Educacional Penedo."
    )
    tbl_nota = Table(
        [[Paragraph("", styles['NotaApresentacao']), Paragraph(nota_texto, styles['NotaApresentacao'])]],
        colWidths=[200, 253.5]
    )
    tbl_nota.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    flowables.append(tbl_nota)

    flowables.append(Spacer(1, 130))
    flowables.append(Paragraph("PENEDO - AL", styles['CoverFooter']))
    flowables.append(Paragraph("2026", styles['CoverFooter']))
    flowables.append(PageBreak())

    # =========================================================================
    # FOLHA 3: SUMÁRIO (CABE RIGOROSAMENTE EM 1 PÁGINA)
    # =========================================================================
    flowables.append(Spacer(1, 10))
    flowables.append(Paragraph("SUMÁRIO", styles['HeadingCenter']))
    flowables.append(Spacer(1, 6))

    toc_entries = [
        ("1. INTRODUÇÃO", "sec_intro", True),
        ("1.1 Contextualização e Problema de Negócio", "sec_intro_1", False),
        ("1.2 Objetivos (Geral e Específicos)", "sec_intro_2", False),
        ("1.3 Justificativa e Relevância Institucional", "sec_intro_3", False),
        ("2. REFERENCIAL TEÓRICO", "sec_teorico", True),
        ("2.1 Saúde Mental no Ensino Superior", "sec_teorico_1", False),
        ("2.2 Sobrecarga e Pressão Acadêmica", "sec_teorico_2", False),
        ("2.3 Vulnerabilidade Socioeconômica e Estresse Financeiro", "sec_teorico_3", False),
        ("2.4 Higiene do Sono e Ritmo Circadiano", "sec_teorico_4", False),
        ("2.5 Procedimentos Estatísticos e Métricas de Efeito", "sec_teorico_5", False),
        ("3. METODOLOGIA", "sec_metodo", True),
        ("3.1 Tipo de Pesquisa e Abordagem Metodológica", "sec_metodo_1", False),
        ("3.2 Coleta, Auditoria e Pipeline de Limpeza", "sec_metodo_2", False),
        ("3.3 Procedimentos Inferenciais e Controle de Erro Tipo I", "sec_metodo_3", False),
        ("4. RESULTADOS E DISCUSSÃO", "sec_resultados", True),
        ("4.1 Análise Descritiva e Exploratória", "sec_resultados_1", False),
        ("4.2 Análise Inferencial e Validação das Hipóteses", "sec_resultados_2", False),
        ("5. RECOMENDAÇÕES PRÁTICAS E PLANO DE AÇÃO", "sec_plano", True),
        ("6. CONSIDERAÇÕES FINAIS", "sec_finais", True),
        ("6.1 Síntese das Contribuições", "sec_finais_1", False),
        ("6.2 Limitações Metodológicas", "sec_finais_2", False),
        ("6.3 Cuidado Ético e Governança de Dados", "sec_finais_3", False),
        ("REFERÊNCIAS", "sec_referencias", True),
        ("APÊNDICE A – Tipagem e Dicionário de Variáveis", "sec_apendice_a", True),
        ("APÊNDICE B – Reprodutibilidade e Código Aberto", "sec_apendice_b", True),
    ]

    toc_table_data = []
    for title, key, is_bold in toc_entries:
        page_str = str(toc_page_numbers.get(key, 5))
        style_t = styles['TOCItemBold'] if is_bold else styles['TOCItem']
        style_p = styles['TOCPageBold'] if is_bold else styles['TOCPage']
        toc_table_data.append([
            Paragraph(title, style_t),
            Paragraph(page_str, style_p)
        ])

    toc_table = Table(toc_table_data, colWidths=[405, 48.5])
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 1.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5),
        ('LINEBELOW', (0, 0), (-1, -1), 0.25, colors.HexColor('#F1F5F9')),
    ]))
    flowables.append(toc_table)
    flowables.append(PageBreak())

    # =========================================================================
    # FOLHA 4: RESUMO EXECUTIVO (ESTRITAMENTE UMA PÁGINA)
    # =========================================================================
    flowables.append(Spacer(1, 4))
    flowables.append(Paragraph("RESUMO EXECUTIVO", styles['ResumoTitle']))
    flowables.append(Paragraph("Diagnóstico Quantitativo e Recomendações Estratégicas de BI Universitário", styles['CaptionAbove']))
    flowables.append(Spacer(1, 3))

    flowables.append(Paragraph("1. Contexto e Formulação do Problema de Business Intelligence", styles['ResumoSection']))
    flowables.append(Paragraph(
        "A evasão, a retenção curricular e o adoecimento psíquico constituem desafios críticos para a gestão estratégica das Instituições de Ensino Superior (IES). No âmbito da disciplina SISB110 (Ciência dos Dados e BI), este projeto desenvolve uma infraestrutura analítica orientada a evidências sobre uma amostra de <b>27.837 estudantes universitários</b> (após higienização rigorosa e auditoria do <i>Student Depression Dataset</i>). O objetivo central é identificar padrões empíricos e fatores associados à prevalência de sintomas depressivos, permitindo que a gestão universitária aloque recursos orçamentários, pedagógicos e de saúde com máxima eficiência e justiça social.",
        styles['ResumoBody']
    ))

    flowables.append(Paragraph("2. Principais Achados Empíricos e Magnitude de Associação", styles['ResumoSection']))
    flowables.append(Paragraph(
        "• <b>Prevalência Amostral Crítica (P1):</b> A proporção amostral com indicativo de depressão é de <b>58,52%</b> (IC 95% de Wilson: [57,94%, 59,10%]; margem de erro de ±0,58%). A taxa de ideação suicida atinge <b>63,26%</b> (17.610 discentes). Esses patamares atipicamente elevados sinalizam forte viés de autosseleção dos respondentes na pesquisa observacional, configurando uma coorte sob elevado alerta psicossocial.",
        styles['ResumoBullet']
    ))
    flowables.append(Paragraph(
        "• <b>Sobrecarga Acadêmica como Efeito de Maior Magnitude (P2):</b> Discentes com indicativo de depressão reportam pressão percebida substantivamente superior (média 3,69 vs 2,36; teste <i>U</i> de Mann-Whitney com <i>p</i> &lt; 1e-300; teste <i>t</i> de Welch com <i>d</i> de Cohen = <b>1,10</b>, efeito grande). A métrica de probabilidade de superioridade atinge <b>aproximadamente 77%</b> (contando empates pela metade), confirmando a sobrecarga como o correlato subjetivo mais pronunciado.",
        styles['ResumoBullet']
    ))
    flowables.append(Paragraph(
        "• <b>Vulnerabilidade Financeira com Gradiente Monotônico Estrito (P4):</b> O estresse financeiro apresenta associação moderada a forte com o desfecho (<i>V</i> de Cramér = <b>0,36</b>; tendência linear de Cochran-Armitage <i>Z</i> = <b>60,67</b>, <i>p</i> &lt; 1e-300). A taxa de depressão sobe continuadamente de <b>31,81%</b> no estrato financeiro mais baixo (nível 1) para <b>81,22%</b> no estrato de máxima restrição material (nível 5).",
        styles['ResumoBullet']
    ))
    flowables.append(Paragraph(
        "• <b>Higiene do Sono e Risco nos Extremos (P3):</b> Estudantes com privação severa (&lt; 5 horas/dia) registram a maior taxa de depressão (<b>64,50%</b>), enquanto aqueles com sono longo (&gt; 8 horas) registram a menor (<b>50,88%</b>). A associação global é estatisticamente significante (χ² = 277,90, <i>p</i> = 6,03e-60), porém fraca (<i>V</i> = <b>0,10</b>) e não-monotônica (a faixa de 7-8h apresenta 59,50%, superior à faixa de 5-6h com 56,89%).",
        styles['ResumoBullet']
    ))
    flowables.append(Paragraph(
        "• <b>Desconexão entre Notas e Bem-Estar Subjetivo (P5):</b> A correlação entre rendimento acadêmico acumulado (CGPA) e satisfação com os estudos é nula na prática (Spearman ρ = <b>-0,047</b>, <i>p</i> = 6,85e-15). Altos coeficientes de rendimento não garantem proteção emocional, e baixas notas não explicam isoladamente a insatisfação com a vida universitária.",
        styles['ResumoBullet']
    ))

    flowables.append(Paragraph("3. Recomendações Institucionais Prioritárias e Plano de Ação", styles['ResumoSection']))
    flowables.append(Paragraph(
        "<b>1. Prioridade Orçamentária e Permanência (P4):</b> Focalizar editais de assistência estudantil, auxílios-moradia e alimentação nos estudantes com estresse financeiro níveis 4 e 5, mitigando a barreira socioeconômica primária.",
        styles['ResumoBullet']
    ))
    flowables.append(Paragraph(
        "<b>2. Governança Pedagógica e Calendários (P2):</b> Reorganizar o planejamento semestral para impedir concentração de avaliações sumativas na mesma semana e padronizar peso curricular entre turmas.",
        styles['ResumoBullet']
    ))
    flowables.append(Paragraph(
        "<b>3. Educação em Higiene do Sono (P3):</b> Implantar oficinas de rotina circadiana e manejo de tempo com apoio das ligas acadêmicas e serviços de saúde.",
        styles['ResumoBullet']
    ))
    flowables.append(Paragraph(
        "<b>4. Acolhimento Universal sem Viés de Desempenho (P5):</b> Desvincular atendimentos psicológicos e núcleos psicopedagógicos de critérios de coeficiente acadêmico.",
        styles['ResumoBullet']
    ))
    flowables.append(PageBreak())

    # =========================================================================
    # FOLHA 5+: ELEMENTOS TEXTUAIS
    # =========================================================================

    # --- 1. INTRODUÇÃO ---
    flowables.append(Paragraph("<a name='sec_intro'/>1. INTRODUÇÃO", styles['Heading1']))
    flowables.append(Paragraph("<a name='sec_intro_1'/><b>1.1 Contextualização e Problema de Negócio</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "O ecossistema universitário contemporâneo vivencia transformações profundas nas demandas acadêmicas, nas condições de subsistência estudantil e nas dinâmicas psicossociais da comunidade discente. A transição para o ensino superior coincide frequentemente com a entrada na fase adulta jovem, momento biológico e social caracterizado por maiores responsabilidades, autonomia financeira restrita, exigência de rendimento intelectual e adaptação a ambientes competitivos.",
        styles['Body']
    ))
    flowables.append(Paragraph(
        "No contexto da gestão universitária e da disciplina SISB110 — Ciência dos Dados e Inteligência Empresarial (UFAL / Campus Arapiraca / Unidade Educacional Penedo), o sofrimento psíquico discente não deve ser encarado apenas como uma demanda de saúde clínica individualizada, mas sim como um indicador crítico de desempenho e sustentabilidade institucional. Taxas elevadas de adoecimento psíquico impactam diretamente os indicadores acadêmicos de permanência, sucesso discente, evasão precoce, trancamento de matrículas e absenteísmo. Desenvolver uma infraestrutura analítica orientada a dados observacionais representa uma estratégia indispensável para orientar a alocação de recursos públicos e planejar políticas de apoio estudantil com embasamento estatístico objetivo.",
        styles['Body']
    ))

    flowables.append(Paragraph("<a name='sec_intro_2'/><b>1.2 Objetivos (Geral e Específicos)</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "O <b>objetivo geral</b> deste trabalho consiste em modelar analiticamente, diagnosticar descritivamente e validar inferencialmente a associação entre fatores acadêmicos, comportamentais e socioeconômicos e a ocorrência de indicativo de depressão em uma coorte de 27.837 estudantes universitários higienizados a partir do <i>Student Depression Dataset</i>.",
        styles['Body']
    ))
    flowables.append(Paragraph("Especificamente, o estudo estrutura-se sobre cinco perguntas formais de inteligência empresarial:", styles['BodyNoIndent']))
    flowables.append(Paragraph("• <b>Pergunta 1 (Prevalência Populacional Amostrada - P1):</b> Qual é a proporção pontual e intervalar estimada de estudantes com indicativo de depressão na população amostrada pela pesquisa?", styles['ResumoBullet']))
    flowables.append(Paragraph("• <b>Pergunta 2 (Sobrecarga Acadêmica - P2):</b> A percepção de pressão acadêmica reportada difere significativamente entre discentes com e sem indicativo de depressão?", styles['ResumoBullet']))
    flowables.append(Paragraph("• <b>Pergunta 3 (Higiene do Sono - P3):</b> A duração habitual do sono está estatisticamente associada à ocorrência de indicativo de depressão entre os estudantes?", styles['ResumoBullet']))
    flowables.append(Paragraph("• <b>Pergunta 4 (Vulnerabilidade Financeira - P4):</b> A prevalência de depressão exibe tendência linear monotônica crescente em função do estresse financeiro experimentado?", styles['ResumoBullet']))
    flowables.append(Paragraph("• <b>Pergunta 5 (Rendimento Acadêmico vs. Satisfação - P5):</b> Existe correlação monotônica ou linear empiricamente relevante entre a satisfação do discente com os estudos e seu rendimento acadêmico acumulado (CGPA)?", styles['ResumoBullet']))

    flowables.append(Paragraph("<a name='sec_intro_3'/><b>1.3 Justificativa e Relevância Institucional</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "A justificativa desta investigação alicerça-se na necessidade de substituir conjecturas intuitivas por evidências empíricas verificáveis no planejamento das ações de assistência e pedagogia universitária. Muitas intervenções institucionais concentram esforços exclusivamente no desempenho estrito de notas (coeficiente de rendimento), supondo que o rendimento intelectual reflita diretamente a satisfação e a estabilidade emocional do discente. A análise rigorosa via Business Intelligence permite testar tais pressupostos, revelando pontos cegos na governança acadêmica e otimizando os orçamentos de assistência estudantil.",
        styles['Body']
    ))

    # --- 2. REFERENCIAL TEÓRICO ---
    flowables.append(Paragraph("<a name='sec_teorico'/>2. REFERENCIAL TEÓRICO", styles['Heading1']))
    flowables.append(Paragraph("<a name='sec_teorico_1'/><b>2.1 Saúde Mental no Ensino Superior e Dados Epidemiológicos</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "A literatura científica global vem documentando uma crise silenciosa e crescente na saúde mental universitária. Na revisão sistemática de ampla repercussão conduzida por Ibrahim et al. (2013), examinando estudos publicados entre 1990 e 2010, constatou-se que a prevalência média ponderada de sintomas depressivos em estudantes universitários alcançou 30,6%, superando sistematicamente as taxas observadas na população em geral. No mesmo sentido, o levantamento epidemiológico internacional do <i>World Mental Health Surveys</i> da Organização Mundial da Saúde (Auerbach et al., 2016) demonstrou que aproximadamente um quinto (20,3%) dos universitários atende a critérios clínicos para transtornos mentais, com severo impacto nas taxas de abandono e evasão do ensino superior.",
        styles['Body']
    ))
    flowables.append(Paragraph(
        "No cenário brasileiro, a V Pesquisa Nacional de Perfil Socioeconômico e Cultural dos Graduandos das IFES (ANDIFES; FONAPRACE, 2019) evidenciou que 83,5% dos graduandos de universidades federais relatam vivenciar dificuldades emocionais que interferem na trajetória acadêmica. Entre os principais sintomas apontados figuram sentimentos de desamparo, ansiedade generalizada e desânimo prolongado, consolidando a saúde mental como eixo indissociável da permanência estudantil no ensino público nacional.",
        styles['Body']
    ))

    flowables.append(Paragraph("<a name='sec_teorico_2'/><b>2.2 Sobrecarga e Percepção de Pressão Acadêmica</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "Em estudo com populações acadêmicas, Beiter et al. (2015) identificaram que o desempenho escolar e a pressão para alcançar sucesso constituem as principais fontes de estresse autorrelatadas por estudantes universitários. A percepção subjetiva de sobrecarga decorre tanto do acúmulo de tarefas e prazos concorrentes quanto da exigência de manutenção de padrões de rendimento para retenção de bolsas e competitividade no mercado de trabalho, potencializando manifestações de ansiedade e depressão.",
        styles['Body']
    ))

    flowables.append(Paragraph("<a name='sec_teorico_3'/><b>2.3 Vulnerabilidade Socioeconômica e Estresse Financeiro</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "A relação entre dificuldades financeiras e sofrimento psíquico discente foi analisada longitudinalmente por Richardson et al. (2017). Os pesquisadores constataram a existência de um círculo vicioso entre estresse por endividamento/insegurança financeira e a piora progressiva dos índices de depressão ao longo da formação acadêmica. A incapacidade de arcar com despesas básicas de subsistência, alimentação, transporte e materiais didáticos constitui uma fonte crônica de tensão que drena a capacidade de enfrentamento cognitivo e emocional do estudante.",
        styles['Body']
    ))

    flowables.append(Paragraph("<a name='sec_teorico_4'/><b>2.4 Higiene do Sono e Ritmo Circadiano</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "A desregulação circadiana e os déficits crônicos de sono representam outro fator amplamente correlacionado a distúrbios de humor no meio discente. O trabalho clássico de Lund et al. (2010) revelou que mais de 60% dos estudantes universitários pesquisados enquadram-se na categoria de maus dormidores pelo Índice de Qualidade do Sono de Pittsburgh (PSQI). A privação habitual de sono compromete a neuroplasticidade, a regulação afetiva e a concentração, exacerbando vulnerabilidades preexistentes.",
        styles['Body']
    ))

    flowables.append(Paragraph("<a name='sec_teorico_5'/><b>2.5 Procedimentos Estatísticos e Métricas de Efeito</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "Para garantir rigor matemático e evitar conclusões espúrias decorrentes do tamanho amostral massivo (N = 27.837), a presente pesquisa fundamenta-se em procedimentos metodológicos consolidados. O Intervalo de Confiança para a prevalência binomial utiliza a formulação de Wilson (1927), reconhecidamente superior à aproximação assintótica de Wald em precisão de cobertura de cauda. A análise de escalas ordinais discretas fundamenta-se no teste não paramétrico de Mann e Whitney (1947), acompanhado pelo teste paramétrico de Welch (1947) para heterocedasticidade assintótica. A intensidade das relações em tabelas de contingência é aferida pelo V de Cramér (1946) e o teste de tendência linear monotônica em proporções segue a formulação clássica de Cochran (1954) e Armitage (1955). Por fim, o controle de inflação do erro Tipo I decorrente de múltiplos testes de hipóteses é formalmente conduzido sob o método sequencial de Holm (1979) e o cálculo padronizado de tamanho de efeito adota a taxonomia de Cohen (1988).",
        styles['Body']
    ))

    # --- 3. METODOLOGIA ---
    flowables.append(Paragraph("<a name='sec_metodo'/>3. METODOLOGIA", styles['Heading1']))
    flowables.append(Paragraph("<a name='sec_metodo_1'/><b>3.1 Tipo de Pesquisa e Abordagem Metodológica</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "Este trabalho adota uma abordagem quantitativa, descritiva e explicativo-inferencial, baseada em levantamento observacional de corte transversal. Os procedimentos foram implementados em Python 3, garantindo total reprodutibilidade computacional através do código-fonte e do Jupyter Notebook <code>analise_depressao.ipynb</code>.",
        styles['Body']
    ))

    flowables.append(Paragraph("<a name='sec_metodo_2'/><b>3.2 Coleta, Auditoria e Pipeline de Limpeza</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "A base primária utilizada foi o <i>Student Depression Dataset</i>, registrado sob licença pública permissiva Apache 2.0 no repositório Kaggle. O arquivo original continha 27.901 observações e 18 variáveis. Conforme documentado no pipeline de engenharia de dados, realizou-se uma auditoria prévia detalhada com contabilidade estrita dos descartes:",
        styles['Body']
    ))
    flowables.append(Paragraph("• <b>Nulos em Financial Stress:</b> 3 registros ausentes (IDs 22377, 68910 e 97610) eliminados sob o princípio de <i>Complete Case Analysis</i>.", styles['ResumoBullet']))
    flowables.append(Paragraph("• <b>Profissionais Não-Estudantes:</b> 31 registros eliminados cujo campo <code>Profession</code> divergia de 'Student', garantindo o foco na população universitária.", styles['ResumoBullet']))
    flowables.append(Paragraph("• <b>Categorias 'Others' em Sono e Dieta:</b> 18 registros em <code>Sleep Duration</code> e 12 registros em <code>Dietary Habits</code> descartados devido a inconsistências de codificação na coleta original.", styles['ResumoBullet']))
    flowables.append(Paragraph("• <b>Descarte de Colunas Quase-Constantes:</b> Remoção dos atributos <code>Work Pressure</code> e <code>Job Satisfaction</code>, sem variabilidade para a coorte discente.", styles['ResumoBullet']))
    flowables.append(Paragraph(
        "Ao término do processo, a amostra higienizada e validada fixou-se em <b>27.837 estudantes universitários</b> (descarte de 64 linhas, correspondendo a apenas 0,23% da base bruta). A base tratada foi gravada em <code>data/student_depression_cleaned.csv</code>.",
        styles['Body']
    ))

    flowables.append(Paragraph("<a name='sec_metodo_3'/><b>3.3 Procedimentos Inferenciais e Controle de Erro Tipo I</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "Adotou-se o nível de significância global pré-fixado de α = 0,05. Para testes em amostras grandes onde z > 37 ou χ² > 1000, os cálculos de p-valor foram conduzidos com funções logarítmicas de sobrevivência (<code>scipy.stats.norm.logsf</code> e <code>scipy.stats.chi2.logsf</code>) para mitigar o underflow em ponto flutuante IEEE 754 de 64 bits, registrando formalmente <code>p &lt; 1e-300</code> quando abaixo do limite de precisão do sistema. Para o controle da taxa de falso-positivo de família (FWER), aplicou-se o procedimento sequencial rejeitador de Holm-Bonferroni sobre as 4 famílias de hipóteses concorrentes.",
        styles['Body']
    ))

    # --- 4. RESULTADOS E DISCUSSÃO ---
    flowables.append(Paragraph("<a name='sec_resultados'/>4. RESULTADOS E DISCUSSÃO", styles['Heading1']))
    flowables.append(Paragraph("<a name='sec_resultados_1'/><b>4.1 Análise Descritiva e Exploratória dos Dados</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "A caracterização da coorte iniciou-se pela extração de métricas de tendência central, dispersão, assimetria e curtose para as variáveis numéricas, apresentadas na Tabela 1. O rendimento acadêmico acumulado (CGPA) variou de 5,01 a 10,00 (após exclusão técnica de 9 zeros inválidos de lançamento), com média de 7,66 e mediana de 7,77. A idade discente concentrou-se majoritariamente entre 20 e 29 anos (mediana 25 anos), com a manutenção justificada de 12 casos até 59 anos compatíveis com pós-graduação.",
        styles['Body']
    ))

    # Tabela 1: Descritiva Numéricas
    flowables.append(Paragraph("Tabela 1 – Estatísticas Descritivas das Variáveis Numéricas (N = 27.837)", styles['CaptionAbove']))
    t1_data = [
        [Paragraph('<b>Variável</b>', styles['TableCellBold']),
         Paragraph('<b>Média</b>', styles['TableCellBold']),
         Paragraph('<b>Desvio Padrão</b>', styles['TableCellBold']),
         Paragraph('<b>Mediana</b>', styles['TableCellBold']),
         Paragraph('<b>IQR</b>', styles['TableCellBold']),
         Paragraph('<b>Assimetria</b>', styles['TableCellBold']),
         Paragraph('<b>Curtose</b>', styles['TableCellBold'])],
        [Paragraph('Idade (Age)', styles['TableCellLeft']), Paragraph('25,82', styles['TableCell']), Paragraph('4,91', styles['TableCell']), Paragraph('25,00', styles['TableCell']), Paragraph('9,00', styles['TableCell']), Paragraph('0,13', styles['TableCell']), Paragraph('-0,85', styles['TableCell'])],
        [Paragraph('Rendimento (CGPA)*', styles['TableCellLeft']), Paragraph('7,66', styles['TableCell']), Paragraph('1,46', styles['TableCell']), Paragraph('7,77', styles['TableCell']), Paragraph('2,63', styles['TableCell']), Paragraph('-0,07', styles['TableCell']), Paragraph('-1,23', styles['TableCell'])],
        [Paragraph('Pressão Acadêmica (0-5)', styles['TableCellLeft']), Paragraph('3,14', styles['TableCell']), Paragraph('1,38', styles['TableCell']), Paragraph('3,00', styles['TableCell']), Paragraph('2,00', styles['TableCell']), Paragraph('-0,13', styles['TableCell']), Paragraph('-1,16', styles['TableCell'])],
        [Paragraph('Satisfação Estudos (0-5)', styles['TableCellLeft']), Paragraph('2,94', styles['TableCell']), Paragraph('1,36', styles['TableCell']), Paragraph('3,00', styles['TableCell']), Paragraph('2,00', styles['TableCell']), Paragraph('0,01', styles['TableCell']), Paragraph('-1,22', styles['TableCell'])],
        [Paragraph('Horas Trabalho/Estudo (0-12)', styles['TableCellLeft']), Paragraph('7,16', styles['TableCell']), Paragraph('3,71', styles['TableCell']), Paragraph('8,00', styles['TableCell']), Paragraph('6,00', styles['TableCell']), Paragraph('-0,46', styles['TableCell']), Paragraph('-1,00', styles['TableCell'])],
        [Paragraph('Estresse Financeiro (1-5)', styles['TableCellLeft']), Paragraph('3,14', styles['TableCell']), Paragraph('1,44', styles['TableCell']), Paragraph('3,00', styles['TableCell']), Paragraph('2,00', styles['TableCell']), Paragraph('-0,13', styles['TableCell']), Paragraph('-1,32', styles['TableCell'])],
    ]
    tbl_num = Table(t1_data, colWidths=[135, 53, 53, 53, 53, 53, 53.5])
    tbl_num.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    flowables.append(tbl_num)
    flowables.append(Paragraph("Fonte: elaboração própria, com dados do Kaggle (*CGPA calculado sobre os 27.828 registros válidos > 0).", styles['SourceBelow']))

    # Tabela 2: Descritiva Categóricas
    flowables.append(Paragraph("Tabela 2 – Frequências Absolutas e Relativas das Variáveis Categóricas (N = 27.837)", styles['CaptionAbove']))
    t2_data = [
        [Paragraph('<b>Variável</b>', styles['TableCellBold']), Paragraph('<b>Categoria</b>', styles['TableCellBold']), Paragraph('<b>Freq. Absoluta (N)</b>', styles['TableCellBold']), Paragraph('<b>Freq. Relativa (%)</b>', styles['TableCellBold'])],
        [Paragraph('Gênero (Gender)', styles['TableCellLeft']), Paragraph('Masculino (Male)<br/>Feminino (Female)', styles['TableCellLeft']), Paragraph('15.511<br/>12.326', styles['TableCell']), Paragraph('55,72%<br/>44,28%', styles['TableCell'])],
        [Paragraph('Duração do Sono', styles['TableCellLeft']), Paragraph('&lt; 5 hours<br/>7-8 hours<br/>5-6 hours<br/>&gt; 8 hours', styles['TableCellLeft']), Paragraph('8.297<br/>7.334<br/>6.172<br/>6.034', styles['TableCell']), Paragraph('29,81%<br/>26,35%<br/>22,17%<br/>21,68%', styles['TableCell'])],
        [Paragraph('Hábitos Alimentares', styles['TableCellLeft']), Paragraph('Unhealthy (Não saudável)<br/>Moderate (Moderado)<br/>Healthy (Saudável)', styles['TableCellLeft']), Paragraph('10.300<br/>9.903<br/>7.634', styles['TableCell']), Paragraph('37,00%<br/>35,57%<br/>27,42%', styles['TableCell'])],
        [Paragraph('Ideação Suicida Prévia', styles['TableCellLeft']), Paragraph('Sim (Yes)<br/>Não (No)', styles['TableCellLeft']), Paragraph('17.610<br/>10.227', styles['TableCell']), Paragraph('63,26%<br/>36,74%', styles['TableCell'])],
        [Paragraph('Histórico Familiar Mental', styles['TableCellLeft']), Paragraph('Não (No)<br/>Sim (Yes)', styles['TableCellLeft']), Paragraph('14.364<br/>13.473', styles['TableCell']), Paragraph('51,60%<br/>48,40%', styles['TableCell'])],
        [Paragraph('Status de Depressão (Desfecho)', styles['TableCellLeft']), Paragraph('Com Indicativo (1)<br/>Sem Indicativo (0)', styles['TableCellLeft']), Paragraph('16.290<br/>11.547', styles['TableCell']), Paragraph('58,52%<br/>41,48%', styles['TableCell'])],
    ]
    tbl_cat = Table(t2_data, colWidths=[140, 153.5, 80, 80])
    tbl_cat.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    flowables.append(tbl_cat)
    flowables.append(Paragraph("Fonte: elaboração própria, com dados do Kaggle.", styles['SourceBelow']))

    # Figura 1: Distribuições Numéricas
    flowables.append(Paragraph("Figura 1 – Distribuições de Densidade e Histogramas das Variáveis Numéricas", styles['CaptionAbove']))
    flowables.append(Image("outputs/01_distribuicoes_numericas.png", width=420, height=252))
    flowables.append(Paragraph("Fonte: elaboração própria, com dados do Kaggle.", styles['SourceBelow']))

    # Figura 2: Rendimento por Sono
    flowables.append(Paragraph("Figura 2 – Rendimento Acadêmico Acumulado (CGPA) por Faixa de Sono", styles['CaptionAbove']))
    flowables.append(Image("outputs/04_cgpa_by_sleep_duration.png", width=360, height=200))
    flowables.append(Paragraph("Fonte: elaboração própria, com dados do Kaggle.", styles['SourceBelow']))

    # Figura 3: Matrizes de Correlação
    flowables.append(Paragraph("Figura 3 – Matrizes de Correlação Linear de Pearson e Monotônica de Spearman", styles['CaptionAbove']))
    flowables.append(Image("outputs/05_correlation_matrices.png", width=430, height=172))
    flowables.append(Paragraph("Fonte: elaboração própria, com dados do Kaggle.", styles['SourceBelow']))

    # Figura 4: Pressupostos Normais
    flowables.append(Paragraph("Figura 4 – Verificação Visual de Pressupostos de Normalidade e Q-Q Plots", styles['CaptionAbove']))
    flowables.append(Image("outputs/06_pressupostos_normais.png", width=360, height=308))
    flowables.append(Paragraph("Fonte: elaboração própria, com dados do Kaggle.", styles['SourceBelow']))

    flowables.append(Paragraph("<a name='sec_resultados_2'/><b>4.2 Análise Inferencial e Validação das Hipóteses de Negócio</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "A testagem estatística confirmou com rigor os padrões de coocorrência e a magnitude de efeito associada ao indicativo de depressão na amostra discente:",
        styles['Body']
    ))

    # P1
    flowables.append(Paragraph("<b>Pergunta 1 (Prevalência de Depressão - P1):</b>", styles['Heading3']))
    flowables.append(Paragraph(
        "A prevalência pontual de discentes com indicativo de depressão foi estimada em <b>58,52%</b>. Pelo método de escore de Wilson a 95% de confiança, o intervalo populacional restrito à coorte situa-se entre <b>[57,94%, 59,10%]</b>, resultando em uma margem de erro extremamente precisa de apenas ±0,58%. A expressiva prevalência indica a relevância de estruturação de ações institucionais permanentes de atenção discente.",
        styles['Body']
    ))

    # P2
    flowables.append(Paragraph("<b>Pergunta 2 (Sobrecarga Acadêmica vs. Depressão - P2):</b>", styles['Heading3']))
    flowables.append(Paragraph(
        "• <i>H₀</i>: A distribuição de pressão acadêmica percebida é idêntica entre estudantes com e sem indicativo de depressão (F_com(x) = F_sem(x)).<br/>"
        "• <i>H₁</i>: A distribuição de pressão acadêmica difere significativamente entre os grupos (F_com(x) ≠ F_sem(x)).",
        styles['BodyNoIndent']
    ))
    flowables.append(Paragraph(
        "O teste não paramétrico de Mann-Whitney rejeitou formalmente <i>H₀</i> (U = 1,45 × 10⁸, z = 78,81, <i>p</i> &lt; 1e-300). A correlação bisserial por postos foi de r_rb = 0,5408 e a probabilidade de superioridade atingiu <b>77,04%</b> (probabilidade de aproximadamente 77% de um discente com depressão registrar escore maior de sobrecarga que um sem depressão, contando empates pela metade). Confirmatoriamente, o teste <i>t</i> de Welch revelou t = 89,21 (<i>p</i> &lt; 1e-300) com tamanho de efeito de Cohen d = 1,0950 (d ≈ 1,10, efeito grande), sendo a sobrecarga o fator de maior magnitude no estudo.",
        styles['Body']
    ))

    # Figura 5: Pressão Acadêmica por Depressão
    flowables.append(Paragraph("Figura 5 – Pressão Acadêmica Percebida por Status de Depressão", styles['CaptionAbove']))
    flowables.append(Image("outputs/03_academic_pressure_by_depression.png", width=330, height=212))
    flowables.append(Paragraph("Fonte: elaboração própria, com dados do Kaggle.", styles['SourceBelow']))

    # P3
    flowables.append(Paragraph("<b>Pergunta 3 (Higiene do Sono vs. Depressão - P3):</b>", styles['Heading3']))
    flowables.append(Paragraph(
        "• <i>H₀</i>: A duração habitual do sono e o indicativo de depressão são independentes.<br/>"
        "• <i>H₁</i>: Existe associação estatística entre a duração do sono e a ocorrência de depressão.",
        styles['BodyNoIndent']
    ))
    flowables.append(Paragraph(
        "O teste Qui-Quadrado de Independência rejeitou a hipótese nula (χ² = 277,90, gl = 3, <i>p</i> = 6,03 × 10⁻⁶⁰). Todavia, a magnitude da associação quantificada pelo V de Cramér revelou-se <b>fraca</b> (V = 0,0999 ≈ 0,10). A taxa de depressão nos extremos foi de <b>64,50%</b> no sono &lt; 5h e de <b>50,88%</b> no sono &gt; 8h, porém exibindo relação não-monotônica nas faixas intermediárias (56,89% em 5-6h vs 59,50% em 7-8h).",
        styles['Body']
    ))

    # Figura 6: Sono vs Depressão
    flowables.append(Paragraph("Figura 6 – Taxa de Depressão por Faixa Habitual de Sono", styles['CaptionAbove']))
    flowables.append(Image("outputs/02_sleep_vs_depression.png", width=340, height=204))
    flowables.append(Paragraph("Fonte: elaboração própria, com dados do Kaggle.", styles['SourceBelow']))

    # P4
    flowables.append(Paragraph("<b>Pergunta 4 (Vulnerabilidade Financeira vs. Depressão - P4):</b>", styles['Heading3']))
    flowables.append(Paragraph(
        "• <i>H₀</i>: A prevalência de depressão independe do nível de estresse financeiro e não apresenta tendência linear.<br/>"
        "• <i>H₁</i>: A prevalência de depressão exibe forte associação e tendência linear monotônica crescente com o estresse financeiro.",
        styles['BodyNoIndent']
    ))
    flowables.append(Paragraph(
        "O teste Qui-Quadrado demonstrou forte dependência (χ² = 3.695,04, gl = 4, <i>p</i> &lt; 1e-300) com coeficiente de associação <b>moderada</b> (V = 0,3643). O teste de tendência linear de Cochran-Armitage confirmou uma progressão estritamente monotônica (Z = 60,67, <i>p</i> &lt; 1e-300): no nível financeiro 1 a prevalência é de 31,81%, elevando-se sequencialmente para 40,32% (nível 2), 59,98% (nível 3), 74,50% (nível 4) e atingindo impressionantes <b>81,22%</b> no nível 5 de vulnerabilidade máxima.",
        styles['Body']
    ))

    # P5
    flowables.append(Paragraph("<b>Pergunta 5 (Satisfação com Estudos vs. Rendimento Acadêmico - P5):</b>", styles['Heading3']))
    flowables.append(Paragraph(
        "• <i>H₀</i>: A correlação populacional entre satisfação acadêmica e CGPA é nula (ρ = 0).<br/>"
        "• <i>H₁</i>: Existe correlação populacional estatisticamente diferente de zero (ρ ≠ 0).",
        styles['BodyNoIndent']
    ))
    flowables.append(Paragraph(
        "O coeficiente de correlação não paramétrica de Spearman registrou ρ = -0,0467 (<i>p</i> = 6,85 × 10⁻¹⁵) e a correlação de Pearson registrou r = -0,0466 (<i>p</i> = 7,52 × 10⁻¹⁵). Embora o volume amostral conceda significância estatística, a magnitude da relação é <b>desprezível e sem relevância prática</b> (|ρ| &lt; 0,10). A inclinação quase nula da reta de regressão na Figura 7 ilustra a total independência empírica entre notas acumuladas e o sentimento de satisfação universitária.",
        styles['Body']
    ))

    # Figura 7: Dispersão Satisfação vs CGPA
    flowables.append(Paragraph("Figura 7 – Gráfico de Dispersão: Satisfação com os Estudos × Rendimento (CGPA)", styles['CaptionAbove']))
    flowables.append(Image("outputs/04_dispersao_satisfacao_cgpa.png", width=360, height=225))
    flowables.append(Paragraph("Fonte: elaboração própria, com dados do Kaggle (N = 27.828, com jitter horizontal e reta linear).", styles['SourceBelow']))

    # Tabela 3: Controle Comparações Múltiplas
    flowables.append(Paragraph("Tabela 3 – Controle de Comparações Múltiplas por Famílias de Hipóteses (Holm-Bonferroni)", styles['CaptionAbove']))
    t3_data = [
        [Paragraph('<b>Família de Hipótese</b>', styles['TableCellBold']),
         Paragraph('<b>p-valor Bruto</b>', styles['TableCellBold']),
         Paragraph('<b>Limiar Holm</b>', styles['TableCellBold']),
         Paragraph('<b>Limiar Bonferroni</b>', styles['TableCellBold']),
         Paragraph('<b>Rejeita H₀?</b>', styles['TableCellBold'])],
        [Paragraph('Família 3: Estresse Financeiro (P4)', styles['TableCellLeft']), Paragraph('p &lt; 1e-300', styles['TableCell']), Paragraph('0,01250', styles['TableCell']), Paragraph('0,01250', styles['TableCell']), Paragraph('Sim (Rejeitada)', styles['TableCellBold'])],
        [Paragraph('Família 1: Pressão Acadêmica (P2)', styles['TableCellLeft']), Paragraph('p &lt; 1e-300', styles['TableCell']), Paragraph('0,01667', styles['TableCell']), Paragraph('0,01250', styles['TableCell']), Paragraph('Sim (Rejeitada)', styles['TableCellBold'])],
        [Paragraph('Família 2: Duração do Sono (P3)', styles['TableCellLeft']), Paragraph('6,03e-60', styles['TableCell']), Paragraph('0,02500', styles['TableCell']), Paragraph('0,01250', styles['TableCell']), Paragraph('Sim (Rejeitada)', styles['TableCellBold'])],
        [Paragraph('Família 4: Satisfação vs CGPA (P5)', styles['TableCellLeft']), Paragraph('6,85e-15', styles['TableCell']), Paragraph('0,05000', styles['TableCell']), Paragraph('0,01250', styles['TableCell']), Paragraph('Sim (Rejeitada)', styles['TableCellBold'])],
    ]
    tbl_multi = Table(t3_data, colWidths=[150, 75, 75, 75, 78.5])
    tbl_multi.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    flowables.append(tbl_multi)
    flowables.append(Paragraph("Fonte: elaboração própria, com dados do Kaggle (FWER controlado a α = 0,05).", styles['SourceBelow']))

    # --- 5. RECOMENDAÇÕES PRÁTICAS E PLANO DE AÇÃO ---
    flowables.append(Paragraph("<a name='sec_plano'/>5. RECOMENDAÇÕES PRÁTICAS E PLANO DE AÇÃO INSTITUCIONAL", styles['Heading1']))
    flowables.append(Paragraph(
        "A transformação dos achados analíticos em valor operacional de Business Intelligence traduz-se em um plano de intervenção priorizado em quatro eixos:",
        styles['Body']
    ))
    flowables.append(Paragraph(
        "<b>Eixo 1 (Prioridade 1 – Política de Permanência e Alívio Financeiro):</b> Como a vulnerabilidade financeira exibiu gradiente de associação de 31,8% a 81,2%, a gestão universitária deve focalizar os editais de bolsas de permanência, moradia e subsídio de alimentação estritamente nos discentes dos estratos 4 e 5. Ações de desoneração de custos diretos (isenção de taxas de materiais e ampliação de refeições nos restaurantes universitários) reduzem a pressão material imediata sobre a saúde discente.",
        styles['Body']
    ))
    flowables.append(Paragraph(
        "<b>Eixo 2 (Prioridade 2 – Gestão Pedagógica e Curricular):</b> Sendo a pressão acadêmica o fator de maior tamanho de efeito (d = 1,10; CLES ≈ 77%), recomenda-se a criação de diretrizes institucionais que impeçam o agendamento de avaliações sumativas de diferentes disciplinas no mesmo intervalo de dias úteis. A implementação de avaliações formativas contínuas e o nivelamento pedagógico de conteúdos reduzem picos de estresse situacional.",
        styles['Body']
    ))
    flowables.append(Paragraph(
        "<b>Eixo 3 (Prioridade 3 – Educação e Higiene do Sono):</b> Promover campanhas informativas periódicas e oficinas de manejo de tempo no início de cada semestre letivo. Espaços de descanso silenciosos nos campi universitários durante intervalos de aulas podem atenuar o cansaço acumulado por discentes em longos deslocamentos pendulares.",
        styles['Body']
    ))
    flowables.append(Paragraph(
        "<b>Eixo 4 (Prioridade 4 – Acolhimento Universal sem Viés de Desempenho):</b> Os serviços de psicologia universitária e as comissões de assistência devem desvincular o acolhimento de exigências de coeficiente acadêmico (CR/CGPA). A pesquisa comprovou que estudantes com alto rendimento acadêmico não estão blindados contra sofrimento psíquico, exigindo canais de busca ativa desmistificados.",
        styles['Body']
    ))

    # --- 6. CONSIDERAÇÕES FINAIS ---
    flowables.append(Paragraph("<a name='sec_finais'/>6. CONSIDERAÇÕES FINAIS", styles['Heading1']))
    flowables.append(Paragraph("<a name='sec_finais_1'/><b>6.1 Síntese das Contribuições</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "O presente relatório executivo consolidou uma abordagem rigorosa de inteligência empresarial aplicada à educação superior. O emprego combinado de procedimentos estatísticos não paramétricos e diagnósticos de sensibilidade demonstrou que a sobrecarga avaliativa e o estresse financeiro são os dois nós críticos de intervenção institucional, superando em magnitude o impacto isolado de horários e rendimento em notas.",
        styles['Body']
    ))

    flowables.append(Paragraph("<a name='sec_finais_2'/><b>6.2 Limitações Metodológicas</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "Ressaltam-se três limitações metodológicas fundamentais que devem orientar a prudência decisória:",
        styles['BodyNoIndent']
    ))
    flowables.append(Paragraph("• <b>Natureza de Corte Transversal:</b> Os dados refletem uma única janela temporal observacional. Não é metodologicamente legítimo estabelecer inferências causais diretas (risco de bicausalidade ou causalidade reversa, onde o estado depressivo pode intensificar a percepção de sobrecarga acadêmica e agravar as finanças).", styles['ResumoBullet']))
    flowables.append(Paragraph("• <b>Instrumento de Autorrelato:</b> As medidas coletadas baseiam-se em questionários autoaplicados com escalas perceptivas discretas, e não em diagnósticos clínicos psiquiátricos estruturados baseados no DSM-5 ou CID-11.", styles['ResumoBullet']))
    flowables.append(Paragraph("• <b>Viés de Autosseleção:</b> A expressiva taxa amostral de ideação suicida (63,26%) e depressão (58,52%) evidencia que discentes em sofrimento tiveram maior propensão espontânea a participar da pesquisa do que estudantes assintomáticos.", styles['ResumoBullet']))

    flowables.append(Paragraph("<a name='sec_finais_3'/><b>6.3 Cuidado Ético e Governança de Dados</b>", styles['Heading2']))
    flowables.append(Paragraph(
        "Sob os preceitos da Lei Geral de Proteção de Dados (LGPD) e da bioética universitária, indicadores sensíveis de ideação suicida e saúde mental devem ser utilizados exclusivamente para o planejamento preventivo e acolhimento em canais voluntários e sigilosos. Sob hipótese alguma tais dados podem ser instrumentalizados para rotulação estigmatizante, monitoramento invasivo ou restrição de direitos acadêmicos.",
        styles['Body']
    ))

    # --- REFERÊNCIAS ---
    flowables.append(Paragraph("<a name='sec_referencias'/>REFERÊNCIAS", styles['Heading1']))
    refs = [
        "ANDIFES; FONAPRACE. <b>V Pesquisa Nacional de Perfil Socioeconômico e Cultural dos (as) Graduandos (as) das IFES - 2018</b>. Brasília: ANDIFES/FONAPRACE, 2019.",
        "ARMITAGE, Peter. Tests for linear trends in proportions and frequencies. <b>Biometrics</b>, v. 11, n. 3, p. 375-386, 1955.",
        "AUERBACH, Randy P. et al. Mental disorders among college students in the World Health Organization World Mental Health Surveys. <b>Psychological Medicine</b>, v. 46, n. 14, p. 2955-2970, 2016. DOI: 10.1017/S0033291716001665.",
        "BEITER, Rebecca et al. The prevalence and correlates of depression, anxiety, and stress in a sample of college students. <b>Journal of Affective Disorders</b>, v. 173, p. 90-96, 2015. DOI: 10.1016/j.jad.2014.10.054.",
        "COCHRAN, William G. Some methods for strengthening the common χ² tests. <b>Biometrics</b>, v. 10, n. 4, p. 417-451, 1954.",
        "COHEN, Jacob. <b>Statistical Power Analysis for the Behavioral Sciences</b>. 2. ed. Hillsdale: Lawrence Erlbaum Associates, 1988.",
        "CRAMÉR, Harald. <b>Mathematical Methods of Statistics</b>. Princeton: Princeton University Press, 1946.",
        "HOLM, Sture. A simple sequentially rejective multiple test procedure. <b>Scandinavian Journal of Statistics</b>, v. 6, n. 2, p. 65-70, 1979.",
        "IBRAHIM, Ahmed K. et al. A systematic review of studies of depression prevalence in university students. <b>Journal of Psychiatric Research</b>, v. 47, n. 3, p. 391-400, 2013. DOI: 10.1016/j.jpsychires.2012.11.015.",
        "LUND, Hannah G. et al. Sleep patterns and predictors of disturbed sleep in a large population of college students. <b>Journal of Adolescent Health</b>, v. 46, n. 2, p. 124-132, 2010. DOI: 10.1016/j.jadohealth.2009.06.021.",
        "MANN, Henry B.; WHITNEY, Donald R. On a test of whether one of two random variables is stochastically larger than the other. <b>The Annals of Mathematical Statistics</b>, v. 18, n. 1, p. 50-60, 1947.",
        "RICHARDSON, Thomas et al. A Longitudinal Study of Financial Difficulties and Mental Health in a National Sample of British Undergraduate Students. <b>Community Mental Health Journal</b>, v. 53, n. 3, p. 344-352, 2017. DOI: 10.1007/s10597-016-0052-0.",
        "WELCH, Bernard L. The generalization of 'Student's' problem when several different population variances are involved. <b>Biometrika</b>, v. 34, n. 1/2, p. 28-35, 1947.",
        "WILSON, Edwin B. Probable inference, the law of succession, and statistical inference. <b>Journal of the American Statistical Association</b>, v. 22, n. 158, p. 209-212, 1927."
    ]
    for r in refs:
        flowables.append(Paragraph(r, styles['RefEntry']))

    # --- APÊNDICES ---
    flowables.append(PageBreak())
    flowables.append(Paragraph("<a name='sec_apendice_a'/>APÊNDICE A – Tipagem Estatística e Dicionário de Variáveis", styles['Heading1']))
    flowables.append(Paragraph(
        "A Tabela 4 sintetiza a tipagem metodológica, a escala de mensuração e os critérios de tratamento formal aplicados a cada coluna do conjunto de dados.",
        styles['Body']
    ))

    t4_data = [
        [Paragraph('<b>Coluna</b>', styles['TableCellBold']),
         Paragraph('<b>Tipo Estatístico</b>', styles['TableCellBold']),
         Paragraph('<b>Escala / Domínio</b>', styles['TableCellBold']),
         Paragraph('<b>Tratamento e Decisão Metodológica</b>', styles['TableCellBold'])],
        [Paragraph('id', styles['TableCellLeft']), Paragraph('Identificador Técnico', styles['TableCellLeft']), Paragraph('Inteiro Único', styles['TableCellLeft']), Paragraph('Mantido para rastreabilidade; 0 duplicatas.', styles['TableCellLeft'])],
        [Paragraph('Gender', styles['TableCellLeft']), Paragraph('Categórica Nominal', styles['TableCellLeft']), Paragraph('Male, Female', styles['TableCellLeft']), Paragraph('Tipada como categoria dicotômica.', styles['TableCellLeft'])],
        [Paragraph('Age', styles['TableCellLeft']), Paragraph('Quantitativa Discreta', styles['TableCellLeft']), Paragraph('18 a 59 anos', styles['TableCellLeft']), Paragraph('12 casos > 43,5 anos (Tukey) e 19 casos (|z| > 3) mantidos sob hipótese discente.', styles['TableCellLeft'])],
        [Paragraph('City', styles['TableCellLeft']), Paragraph('Categórica Nominal', styles['TableCellLeft']), Paragraph('52 cidades', styles['TableCellLeft']), Paragraph('Tipada como texto/categoria nominal.', styles['TableCellLeft'])],
        [Paragraph('Profession', styles['TableCellLeft']), Paragraph('Categórica Nominal', styles['TableCellLeft']), Paragraph('Student', styles['TableCellLeft']), Paragraph('31 profissionais não-estudantes removidos.', styles['TableCellLeft'])],
        [Paragraph('Academic Pressure', styles['TableCellLeft']), Paragraph('Qualitativa Ordinal', styles['TableCellLeft']), Paragraph('Escala 0 a 5', styles['TableCellLeft']), Paragraph('9 zeros analisados por sensibilidade (dif: 0,0010 ponto na média; mediana inalterada em 3,0).', styles['TableCellLeft'])],
        [Paragraph('CGPA', styles['TableCellLeft']), Paragraph('Quantitativa Razão', styles['TableCellLeft']), Paragraph('0,0 a 10,0', styles['TableCellLeft']), Paragraph('9 zeros inválidos excluídos das análises específicas de rendimento (N = 27.828).', styles['TableCellLeft'])],
        [Paragraph('Study Satisfaction', styles['TableCellLeft']), Paragraph('Qualitativa Ordinal', styles['TableCellLeft']), Paragraph('Escala 0 a 5', styles['TableCellLeft']), Paragraph('10 zeros analisados por sensibilidade (dif: 0,0011 ponto na média; mediana inalterada em 3,0).', styles['TableCellLeft'])],
        [Paragraph('Sleep Duration', styles['TableCellLeft']), Paragraph('Categórica Ordinal', styles['TableCellLeft']), Paragraph('4 faixas de horas', styles['TableCellLeft']), Paragraph('18 registros \'Others\' excluídos por ruído de codificação.', styles['TableCellLeft'])],
        [Paragraph('Dietary Habits', styles['TableCellLeft']), Paragraph('Categórica Ordinal', styles['TableCellLeft']), Paragraph('3 estratos alimentares', styles['TableCellLeft']), Paragraph('12 registros \'Others\' excluídos por ruído de codificação.', styles['TableCellLeft'])],
        [Paragraph('Degree', styles['TableCellLeft']), Paragraph('Categórica Nominal', styles['TableCellLeft']), Paragraph('28 cursos/titulações', styles['TableCellLeft']), Paragraph('Tipada como texto/categoria nominal.', styles['TableCellLeft'])],
        [Paragraph('Suicidal Thoughts', styles['TableCellLeft']), Paragraph('Categórica Nominal', styles['TableCellLeft']), Paragraph('Yes, No', styles['TableCellLeft']), Paragraph('Indicador de alerta institucional para acolhimento preventivo.', styles['TableCellLeft'])],
        [Paragraph('Work/Study Hours', styles['TableCellLeft']), Paragraph('Quantitativa Discreta', styles['TableCellLeft']), Paragraph('0 a 12 horas/dia', styles['TableCellLeft']), Paragraph('1.700 casos na bruta (6,09%) e 1.697 casos na tratada (6,10%) mantidos sob suposição de férias.', styles['TableCellLeft'])],
        [Paragraph('Financial Stress', styles['TableCellLeft']), Paragraph('Qualitativa Ordinal', styles['TableCellLeft']), Paragraph('Escala 1 a 5', styles['TableCellLeft']), Paragraph('3 nulos excluídos por complete case analysis.', styles['TableCellLeft'])],
        [Paragraph('Family History', styles['TableCellLeft']), Paragraph('Categórica Nominal', styles['TableCellLeft']), Paragraph('Yes, No', styles['TableCellLeft']), Paragraph('Tipada como categoria binária de suporte epidemiológico.', styles['TableCellLeft'])],
        [Paragraph('Depression', styles['TableCellLeft']), Paragraph('Binária / Dicotômica', styles['TableCellLeft']), Paragraph('0 = Não, 1 = Sim', styles['TableCellLeft']), Paragraph('Desfecho principal modelado nas análises inferenciais.', styles['TableCellLeft'])],
    ]
    tbl_dic = Table(t4_data, colWidths=[80, 85, 80, 208.5])
    tbl_dic.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    flowables.append(tbl_dic)
    flowables.append(Paragraph("Fonte: elaboração própria, com dados do Kaggle.", styles['SourceBelow']))

    flowables.append(Spacer(1, 10))
    flowables.append(Paragraph("<a name='sec_apendice_b'/>APÊNDICE B – Reprodutibilidade e Código Aberto", styles['Heading1']))
    flowables.append(Paragraph(
        "Em cumprimento aos padrões de reprodutibilidade e ciência aberta, todo o código computacional, pipeline de higienização, rotinas estatísticas em Python e arquivos gráficos estão publicamente acessíveis no repositório oficial do projeto:",
        styles['Body']
    ))
    flowables.append(Paragraph(
        "• <b>Repositório GitHub:</b> <font color='#1A365D'><u>https://github.com/brunomartinsgg/sisb110-depressao-estudantes</u></font>",
        styles['BulletBody']
    ))
    flowables.append(Paragraph(
        "• <b>Notebook de Análise:</b> <code>analise_depressao.ipynb</code> (executável sequencialmente de ponta a ponta).",
        styles['BulletBody']
    ))
    flowables.append(Paragraph(
        "• <b>Script de Compilação do PDF:</b> <code>generate_pdf.py</code> (ReportLab e DejaVu Sans nativo).",
        styles['BulletBody']
    ))
    flowables.append(Paragraph(
        "• <b>Ambiente de Execução:</b> Testado e validado em Python 3.14 sob Windows PowerShell.",
        styles['BulletBody']
    ))

    return flowables


def run_compilation():
    pdf_filename = "relatorio_executivo_bi.pdf"
    
    # -------------------------------------------------------------------------
    # Passo 1: Compilação Preliminar para Detecção de Páginas Exatas do Sumário
    # -------------------------------------------------------------------------
    print("Passo 1: Compilando rascunho preliminar para mapeamento de páginas...")
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=85.04,   # 3.0 cm
        rightMargin=56.69,  # 2.0 cm
        topMargin=85.04,    # 3.0 cm
        bottomMargin=56.69  # 2.0 cm
    )
    draft_flowables = build_pdf_flowables()
    doc.build(draft_flowables, canvasmaker=ABNTCanvas)

    # Inspeciona com PyMuPDF para encontrar a página exata de cada seção
    doc_fitz = pymupdf.open(pdf_filename)
    section_targets = [
        ("1. INTRODUÇÃO", "sec_intro"),
        ("1.1 Contextualização", "sec_intro_1"),
        ("1.2 Objetivos", "sec_intro_2"),
        ("1.3 Justificativa", "sec_intro_3"),
        ("2. REFERENCIAL TEÓRICO", "sec_teorico"),
        ("2.1 Saúde Mental", "sec_teorico_1"),
        ("2.2 Sobrecarga", "sec_teorico_2"),
        ("2.3 Vulnerabilidade Socioeconômica", "sec_teorico_3"),
        ("2.4 Higiene do Sono", "sec_teorico_4"),
        ("2.5 Procedimentos Estatísticos", "sec_teorico_5"),
        ("3. METODOLOGIA", "sec_metodo"),
        ("3.1 Tipo de Pesquisa", "sec_metodo_1"),
        ("3.2 Coleta, Auditoria", "sec_metodo_2"),
        ("3.3 Procedimentos Inferenciais", "sec_metodo_3"),
        ("4. RESULTADOS E DISCUSSÃO", "sec_resultados"),
        ("4.1 Análise Descritiva", "sec_resultados_1"),
        ("4.2 Análise Inferencial", "sec_resultados_2"),
        ("5. RECOMENDAÇÕES PRÁTICAS", "sec_plano"),
        ("6. CONSIDERAÇÕES FINAIS", "sec_finais"),
        ("6.1 Síntese das Contribuições", "sec_finais_1"),
        ("6.2 Limitações Metodológicas", "sec_finais_2"),
        ("6.3 Cuidado Ético", "sec_finais_3"),
        ("REFERÊNCIAS", "sec_referencias"),
        ("APÊNDICE A", "sec_apendice_a"),
        ("APÊNDICE B", "sec_apendice_b"),
    ]

    detected_pages = {}
    for target_label, key in section_targets:
        found_page = None
        for page_idx in range(4, len(doc_fitz)):  # a partir da página 5
            page_text = doc_fitz[page_idx].get_text("text")
            if target_label in page_text:
                found_page = page_idx + 1
                break
        if found_page:
            detected_pages[key] = found_page
        else:
            detected_pages[key] = 5
    doc_fitz.close()

    print("Mapeamento dinâmico de páginas concluído:")
    for k, v in detected_pages.items():
        print(f"  {k}: página {v}")

    # -------------------------------------------------------------------------
    # Passo 2: Compilação Final com o Sumário 100% Preciso
    # -------------------------------------------------------------------------
    print("\nPasso 2: Compilando versão final com Sumário sincronizado...")
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=85.04,
        rightMargin=56.69,
        topMargin=85.04,
        bottomMargin=56.69
    )
    final_flowables = build_pdf_flowables(toc_page_numbers=detected_pages)
    doc.build(final_flowables, canvasmaker=ABNTCanvas)
    print(f"Documento '{pdf_filename}' gerado com sucesso!")


if __name__ == "__main__":
    run_compilation()
