# SISB110 — Ciência dos Dados e Inteligência Empresarial (UFAL)
## Análise Descritiva, Inferencial e Relatório de BI: Saúde Mental Estudantil

Este repositório contém o projeto prático individual desenvolvido para a disciplina **SISB110 — Ciência dos Dados e Inteligência Empresarial** da Universidade Federal de Alagoas (UFAL).

O projeto adota uma perspectiva de **Business Intelligence (BI) para Gestão Universitária**, investigando como fatores de sobrecarga acadêmica, higiene do sono, estresse financeiro e satisfação estão associados à ocorrência de indicativo de depressão entre estudantes.

* **Autor:** Bruno Martins Gomes — SISB110, UFAL
* **Repositório Público do Projeto:** [https://github.com/brunomartinsgg/sisb110-depressao-estudantes](https://github.com/brunomartinsgg/sisb110-depressao-estudantes)
* **Relatório Acadêmico-Executivo em PDF:** [`relatorio_executivo_bi.pdf`](relatorio_executivo_bi.pdf) (20 páginas, padrão ABNT / modelo oficial UFAL Penedo)

### Principais Resultados
* **Sobrecarga Acadêmica como Efeito de Maior Magnitude:** Estudantes com indicativo de depressão reportam maior pressão acadêmica percebida (média de **3,69** vs. **2,36**; Mann-Whitney $U = 1,45 \times 10^8$, $p < 0,0001$, $d = 1,10$), com probabilidade de superioridade de **aproximadamente 77%, contando empates pela metade**.
* **Estresse Financeiro como Fator Fortemente Associado:** Exibe associação moderada ($V = 0,36$) e forte tendência linear monotônica (Cochran-Armitage $Z = 60,67$, $p < 0,0001$), com a taxa de depressão crescendo de forma acentuada de **31,81%** no nível 1 para **81,23%** no nível 5.
* **Prevalência Amostral Estimada:** A proporção de discentes com indicativo de depressão na amostra é de **58,52%** (IC 95% de Wilson: **[57,94%, 59,10%]**, margem de erro de ±0,58%).
* **Desconexão entre Notas e Satisfação:** O coeficiente de rendimento (CGPA) não possui relevância prática substantiva com a satisfação com os estudos (Spearman $\rho = -0,0467$, $p < 0,0001$; magnitude desprezível $\lvert\rho\rvert < 0,10$).

---

### 1. Estrutura do Projeto

```text
├── data/
│   ├── Student_Depression_Dataset.csv   # Base de dados bruta (27.901 linhas, Kaggle/Hugging Face, Apache 2.0)
│   └── student_depression_cleaned.csv   # Base tratada e validada (27.837 estudantes)
├── outputs/                             # Tabelas e gráficos gerados para o Relatório Executivo
│   ├── 01_distribuicoes_numericas.png
│   ├── 02_sleep_vs_depression.png
│   ├── 03_academic_pressure_by_depression.png
│   ├── 04_cgpa_by_sleep_duration.png
│   ├── 04_dispersao_satisfacao_cgpa.png # Gráfico de dispersão P5 com jitter e tendência linear
│   ├── 05_correlation_matrices.png
│   ├── 06_pressupostos_normais.png
│   ├── tabela_descritiva_numericas.csv
│   ├── tabela_descritiva_categoricas.csv
│   ├── tabela_bivariada_sleep_depression.csv
│   ├── tabela_bivariada_fin_depression.csv
│   ├── tabela_sensibilidade_cgpa.csv
│   ├── matriz_correlacao_pearson.csv
│   └── matriz_correlacao_spearman.csv
├── analise_depressao.ipynb             # Notebook reprodutível executável de ponta a ponta (Etapas I a IV)
├── generate_pdf.py                     # Script para compilação do Relatório Executivo em PDF (ReportLab)
├── relatorio_executivo_bi.pdf          # Relatório Acadêmico-Executivo Final em PDF (20 páginas, padrão ABNT / UFAL)
├── AGENTE_CIENTISTA_DADOS.md           # Planejamento, decisões metodológicas e log de progresso
├── requirements.txt                    # Dependências do ambiente Python (inclui reportlab e pymupdf)
├── .gitignore                          # Configuração de arquivos ignorados no versionamento
└── README.md                           # Instruções de reprodução e contexto
```

---

### 2. Origem dos Dados e Como Obter o Arquivo

* **Fonte Primária Original:** *Student Depression Dataset* no Kaggle ([link oficial no Kaggle](https://www.kaggle.com/datasets/hopesb/student-depression-dataset)), publicado por Shodolamu Opeyemi (`hopesb`).
* **Licença do Dataset:** Licença **Apache 2.0** formalmente registrada no Kaggle (código aberto permissivo, que autoriza reprodução, redistribuição e modificação).
* **Espelho Utilizado no Projeto:** Repositório no Hugging Face Datasets ([urmah/student-depression-analysis](https://huggingface.co/datasets/urmah/student-depression-analysis)).
* **Volume Bruto:** 27.901 linhas e 18 colunas (conferido: 27.901 linhas e 18 colunas, compatível com a versão integral do dataset).

#### Como baixar o arquivo CSV:
1. Caso não esteja na pasta, baixe diretamente o arquivo `Student_Depression_Dataset.csv` pelo [Kaggle](https://www.kaggle.com/datasets/hopesb/student-depression-dataset) ou pelo endpoint do Hugging Face:
   ```bash
   # Opção via linha de comando:
   curl -L -o data/Student_Depression_Dataset.csv "https://huggingface.co/datasets/urmah/student-depression-analysis/resolve/main/Student_Depression_Dataset.csv"
   ```
2. Certifique-se de que o arquivo esteja localizado em `data/Student_Depression_Dataset.csv`.

---

### 3. Como Reproduzir o Projeto

#### Pré-requisitos
* Python 3.14 (testado nesta versão)
* Gerenciador de pacotes `pip`

#### Instalação das Dependências
No terminal, dentro da pasta raiz do projeto, instale os pacotes listados em `requirements.txt`:

```bash
pip install -r requirements.txt
```

#### Execução do Notebook ("Restart & Run All")
Abra e execute o notebook `analise_depressao.ipynb` em seu ambiente preferido (Jupyter Lab, VS Code, Google Colab ou Jupyter Notebook) e clique em **Kernel -> Restart & Run All**.

O notebook roda do início ao fim sem intervenções:
1. Carrega a base bruta de `data/Student_Depression_Dataset.csv`.
2. Executa a limpeza justificada (filtragem de não-estudantes, exclusão de nulos pontuais e categorias espúrias 'Others', descarte de colunas quase constantes e tratamento dos zeros de CGPA).
3. Produz todas as tabelas descritivas univariadas e bivariadas.
4. Conduz a análise inferencial completa (IC de Wilson, Mann-Whitney U, Welch, Qui-Quadrado, Cochran-Armitage e Spearman) com seus tamanhos de efeito e controle de comparações múltiplas.
5. Salva todas as figuras em alta resolução (300 DPI) — incluindo o gráfico de dispersão com jitter horizontal e reta de tendência linear de P5 — e tabelas em formato CSV na pasta `outputs/`.

#### Como Regenerar o Relatório em PDF
Para recompilar o arquivo [`relatorio_executivo_bi.pdf`](relatorio_executivo_bi.pdf):

```bash
python generate_pdf.py
```

O script gera o documento completo de 20 páginas formatado estritamente nas normas ABNT e no padrão institucional da UFAL (Campus Arapiraca / Unidade Educacional Penedo), utilizando a biblioteca `reportlab`, fonte vetorial *DejaVu Sans* nativa do `matplotlib` e compilação em duas passadas com `pymupdf` para mapeamento dinâmico e 100% exato dos números de página no Sumário. O Resumo Executivo fica contido integralmente em 1 página (página 4), e a numeração visível das páginas tem início formal na página textual 5 (Seção 1 - Introdução).

---

### 4. Resumo dos Procedimentos Estatísticos Aplicados

| Questão de Negócio | Variáveis | Hipóteses Formais ($H_0$ e $H_1$) | Procedimento Principal | Confirmação / Tamanho de Efeito | Decisão ($\alpha = 0,05$) |
|---|---|---|---|---|---|
| **P1: Prevalência de Depressão** | `Depression` (0/1) | — | IC 95% de Wilson | Intervalo: **[57,94%, 59,10%]** ($p = 58,52\%$) | Estimativa populacional com margem de erro de $\pm 0,58\%$ |
| **P2: Pressão Acadêmica vs Depressão** | `Academic Pressure` (0-5) × `Depression` | $H_0: F_{\text{com}}(x) = F_{\text{sem}}(x)$<br>$H_1: F_{\text{com}}(x) \neq F_{\text{sem}}(x)$ | Teste U de Mann-Whitney ($U = 1,45 \times 10^8$, $p < 0,0001$) | $r_{rb} = 0,5408$; **probabilidade de superioridade de aproximadamente 77%, contando empates pela metade**. Welch: $t = 89,21$, $d = 1,10$. | **Rejeita $H_0$**; Associação de grande magnitude |
| **P3: Duração do Sono vs Depressão** | `Sleep Duration` (4 faixas) × `Depression` | $H_0$: Variáveis independentes<br>$H_1$: Variáveis associadas | Qui-Quadrado de Independência ($\chi^2 = 277,90$, $p < 0,0001$, $gl=3$) | $V$ de Cramér = **0,10** (associação fraca). Taxas: $<5$h ($64,5\%$), $5\text{--}6$h ($56,9\%$), $7\text{--}8$h ($59,5\%$), $>8$h ($50,9\%$). | **Rejeita $H_0$**; Associação fraca e não-monotônica |
| **P4: Estresse Financeiro vs Depressão** | `Financial Stress` (1-5) × `Depression` | $H_0$: Independência e sem tendência<br>$H_1$: Tendência linear/monotônica crescente | Qui-Quadrado ($\chi^2 = 3695,04$, $p < 0,0001$, $gl=4$) | $V$ de Cramér = **0,36** (associação moderada); Tendência de Cochran-Armitage: $Z = 60,67$, $p < 0,0001$ (tendência forte, de $31,8\%$ a $81,2\%$). | **Rejeita $H_0$**; Gradiente estrito crescente |
| **P5: Satisfação com Estudos vs CGPA** | `Study Satisfaction` (0-5) × `CGPA` (0-10) | $H_0: \rho = 0$<br>$H_1: \rho \neq 0$ | Correlação de Spearman ($\rho = -0,0467$, $p < 0,0001$) | Correlação de Pearson ($r = -0,0466$, $p < 0,0001$). Magnitude negligenciável ($\lvert\rho\rvert < 0,10$). Gráfico de dispersão com jitter salvo em `outputs/04_dispersao_satisfacao_cgpa.png`. | **Rejeita $H_0$** matemático, mas **efeito prático negligenciável** |

*Nota de Comparações Múltiplas:* São 4 famílias de hipóteses (P1 é IC; P2 possui dois testes para a mesma hipótese). Ajustando para as famílias via método de Holm-Bonferroni, todos os testes mantêm significância estatística ($p < 10^{-14}$).

---

### 5. Limitações Metodológicas e Cuidado Ético

* **Associação vs. Causalidade:** Os dados são observacionais e de corte transversal; nenhuma inferência causal é estabelecida, adotando-se estritamente o termo "associação" devido à plausibilidade de causalidade reversa (ex.: sofrimento psíquico amplificando a percepção de sobrecarga acadêmica e dificuldades financeiras).
* **Ausência de Diagnóstico Clínico:** A variável de desfecho provém de questionário autoaplicado, e não de instrumento clínico estruturado por psiquiatras/psicólogos baseado em manuais diagnósticos (DSM-5 / CID-11).
* **Viés de Resposta e Não Representatividade:** As taxas elevadas encontradas ($58,5\%$ de depressão e $63,3\%$ de pensamentos suicidas) revelam provável viés de autosseleção da amostra, que não deve ser tomada como representativa de toda a comunidade acadêmica.
* **Cuidado Ético em Saúde Mental:** Variáveis de ideação suicida e depressão devem ser interpretadas sob estrito compromisso ético e humanizado, orientadas para subsidiar redes de acolhimento psicossocial institucional e políticas de permanência estudantil, nunca para estigmatização de estudantes.
