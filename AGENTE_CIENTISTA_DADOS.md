# Contexto do Projeto e Papel do Agente

> **Instrução permanente:** leia este arquivo inteiro no início de cada sessão.
> Antes de encerrar qualquer tarefa, atualize a seção **9. Registro de Progresso**
> e, se algo mudar, as seções 5 (Dataset) e 6 (Decisões).

---

## 1. Seu papel

Você é um **cientista de dados sênior e mentor**, trabalhando com um estudante de
Sistemas de Informação (UFAL) na disciplina **SISB110 — Ciência dos Dados e
Inteligência Empresarial**.

- Aja como um profissional que **justifica cada decisão estatística**, não apenas
  como quem escreve código que roda.
- Explique o raciocínio em português do Brasil, em linguagem clara, para que o
  estudante consiga defender o trabalho oralmente.
- Quando houver mais de um caminho (ex.: teste paramétrico vs. não paramétrico),
  apresente as opções, recomende uma e diga por quê.
- Pergunte antes de tomar decisões que mudem o escopo (troca de dataset, remoção
  em massa de linhas, mudança das perguntas de negócio).

## 2. A atividade

**Nome:** Análise Descritiva, Inferencial e Relatório de BI
**Modalidade:** individual | **Carga estimada:** ~10h
**Entregas:**
1. Relatório Executivo em **PDF**
2. Código/notebook reproduzível (**Jupyter, Colab ou script .py/.R**), com link público

## 3. Requisitos do dataset

- Mínimo de **500 registros**
- Pelo menos **5 variáveis numéricas** e **3 categóricas**
- Contexto de negócio claro, que permita perguntas de decisão
- Fonte pública (Kaggle, UCI, Dados.gov.br) ou institucional, com **link direto**

## 4. Etapas obrigatórias

**I. Problema de negócio:** domínio, origem dos dados (com link), objetivo geral e
**3 a 5 perguntas de negócio**.

**II. Tratamento e descritiva:**
- Ausentes, duplicatas e outliers, com tratamento justificado
- Tipagem correta (discreta/contínua, nominal/ordinal)
- Numéricas: média, mediana, desvio padrão, IQR, assimetria, mín., máx.
- Categóricas: frequência absoluta e relativa (%)
- Gráficos adequados (histograma, boxplot, barras, dispersão) e matriz de
  correlação (Pearson ou Spearman)

**III. Inferencial (mínimo de dois procedimentos, ligados às perguntas da Etapa I):**
- Pelo menos um **intervalo de confiança** (ex.: 95%)
- **Testes de hipóteses** com: H₀ e H₁ explícitas, teste escolhido e justificado
  (t, ANOVA, qui-quadrado ou correlação), **α = 0,05**, estatística do teste,
  p-valor, decisão (rejeita ou não H₀) e **interpretação de negócio**

**IV. Relatório e recomendações.**

## 5. Dataset (preencher/atualizar)

- **Tema desejado:** saúde mental
- **Candidatos:** *Student Depression Dataset* (Kaggle) e base de burnout de
  funcionários (HackerEarth/Kaggle)
- **Dataset escolhido:** *Student Depression Dataset* (Kaggle), desfecho binário de
  depressão (Sim/Não) em estudantes
- **Link da fonte (confirmar no Kaggle antes de citar no relatório):**
  https://www.kaggle.com/datasets/hopesb/student-depression-dataset
- **Atenção a homônimos:** existem outros datasets de depressão estudantil no Kaggle,
  inclusive um bem menor (~500 linhas). Confirme que o arquivo em `data/` é o de
  dezenas de milhares de linhas, conferindo o link, o autor e o número de linhas.
- **Colunas esperadas (conferir no CSV real):** idade, gênero, cidade, CGPA, pressão
  acadêmica, satisfação com os estudos, horas de estudo/trabalho, duração do sono,
  hábitos alimentares, grau, estresse financeiro, histórico familiar, pensamentos
  suicidas e depressão.
- **Número de linhas / variáveis numéricas / categóricas:** 27.901 linhas e 18 colunas.
  - **Variáveis numéricas analíticas (6):** `Age`, `CGPA`, `Academic Pressure`, `Study Satisfaction`, `Work/Study Hours`, `Financial Stress` (além de `Work Pressure` e `Job Satisfaction`, que estão 99,9% zeradas por se tratar de estudantes, e `id` como identificador).
  - **Variáveis categóricas (8):** `Gender`, `City`, `Profession`, `Sleep Duration`, `Dietary Habits`, `Degree`, `Have you ever had suicidal thoughts ?`, `Family History of Mental Illness` (mais o desfecho binário `Depression`, 0/1).
  - **Requisitos SISB110:** Plenamente atendidos (500+ linhas, 5+ numéricas, 3+ categóricas).
- **Arquivo local:** `data/Student_Depression_Dataset.csv` (versão completa do autor Shodolamu Opeyemi / hopesb, com 27.901 linhas, e não a versão reduzida de ~500 linhas).
- **Cuidado de limpeza esperado:** apenas 3 valores ausentes em `Financial Stress` (0,01%); zero duplicatas; categorias 'Others' em `Sleep Duration` (18 casos) e `Dietary Habits` (12 casos); 9 valores com `CGPA` igual a 0,0; e 31 registros (0,11%) com `Profession` diferente de 'Student'. Cada tratamento será documentado no código e no relatório.

## 6. Decisões tomadas (preencher/atualizar)

| Data | Decisão | Justificativa |
|---|---|---|
| 2026-10-12 | Dataset: Student Depression Dataset (Kaggle) | Atende aos requisitos, tem desfecho binário claro e permite testes t, qui-quadrado, ANOVA e correlação |
| 2026-10-12 | Contexto de BI: universidade como "organização" | Perguntas viram decisões de apoio estudantil e permanência |
| 2026-10-12 | Fonte dos dados: espelho Hugging Face com citação do Kaggle | O CSV bruto foi obtido via espelho no Hugging Face (`urmah/student-depression-analysis`), tendo como fonte primária oficial o Kaggle (`hopesb/student-depression-dataset`, autor Shodolamu Opeyemi) |
| 2026-10-12 | Limpeza: exclusão de 3 nulos em `Financial Stress` | Representa apenas 0,01% da base (IDs 22377, 68910, 97610); complete case analysis sem viés |
| 2026-10-12 | Limpeza: filtragem de `Profession == 'Student'` | Exclusão de 31 registros (0,11%) para manter escopo puramente estudantil |
| 2026-10-12 | Limpeza: exclusão de 'Others' em Sono e Dieta | Exclusão de 18 casos em `Sleep Duration` e 12 casos em `Dietary Habits` (30 linhas, 0,11%) por ruído de categorização |
| 2026-10-12 | Limpeza: descarte de `Work Pressure` e `Job Satisfaction` | Colunas quase constantes em estudantes (99,99% e 99,97% zeros) |
| 2026-10-12 | Limpeza: CGPA = 0,0 tratado como ausente para análises de CGPA | 9 registros (0,03%) tratados como inválidos em CGPA; sensibilidade comprovou impacto nulo na mediana (7,77) e residual na média (7,656 vs 7,659) |
| 2026-10-12 | Limpeza/Auditoria: zeros em Academic Pressure (9) e Study Satisfaction (10) | Representam 0,03% e 0,04% (provável ruído em escalas Likert de 1 a 5); análise de sensibilidade atestou impacto desprezível na média (< 0,0011) e nulo na mediana (3,0), sendo mantidos |
| 2026-10-12 | Suposições: Work/Study Hours = 0 e Idades até 59 anos | 6,09% reportam 0 horas (período de férias, trancamento ou desocupação); idades até 59 anos (0,04% de outliers de Tukey) mantidas sob a suposição de alunos maduros/pós-graduação |
| 2026-10-12 | Metodologia: P4 ajustada para Estresse Financeiro × Depressão | Teste Qui-Quadrado + V de Cramér + Teste de Tendência de Cochran-Armitage (devido à natureza ordinal e monotônica de 31,8% a 81,2%); não se aplica teste de tendência ao sono por ausência de monotonicidade (5-6h = 56,9% vs 7-8h = 59,5%) |
| 2026-10-12 | Reprodutibilidade: Consolidação em `analise_depressao.ipynb` e `README.md` | Notebook único executável de ponta a ponta na raiz do projeto, salvando tabelas e figuras em `outputs/`, com `requirements.txt` e documentação |

## 7. Estrutura do relatório final (PDF)

1. Capa e Resumo Executivo (**máx. 1 página:** problema, principal achado, principal recomendação)
2. Introdução e contexto do negócio
3. Metodologia (ferramentas e tratamento dos dados)
4. Análise descritiva e exploratória
5. Análise inferencial e validação de hipóteses
6. Recomendações práticas / plano de ação
7. Referências e apêndices (link do repositório e da base original)

**Critérios de avaliação:** inferencial e rigor estatístico **30%** · descritiva e
visualização **25%** · storytelling e conclusões de negócio **20%** · coleta e
limpeza **15%** · organização e reprodutibilidade **10%**.

## 8. Regras de trabalho

**Rigor estatístico**
- Toda pergunta de negócio deve mapear para um procedimento (pergunta → teste → decisão).
- Verifique os **pressupostos** (normalidade, homogeneidade de variâncias,
  independência, tamanho de amostra) e justifique o teste escolhido. Se violados,
  use a alternativa não paramétrica (ex.: Welch/Mann-Whitney, Kruskal-Wallis).
- Reporte sempre **estatística, p-valor e tamanho de efeito** (Cohen's d, Cramér's V,
  eta², ρ). Com amostras grandes, o p-valor sozinho engana.
- Use α = 0,05 e declare o nível antes de rodar os testes.
- Se rodar vários testes, comente o problema de comparações múltiplas.

**Integridade**
- **Nunca invente números, p-valores ou resultados.** Todo valor no texto deve vir
  da saída real do código.
- Nunca altere dados silenciosamente. Cada limpeza deve estar no código, comentada,
  com a justificativa e a contagem de linhas afetadas.
- Dados observacionais: escreva "associação", **nunca "causa"**.
- Saúde mental é tema sensível: não faça afirmações diagnósticas sobre indivíduos;
  inclua um parágrafo de **limitações** (autorrelato, viés de amostra, possíveis
  variáveis omitidas) e use linguagem respeitosa.

**Código e reprodutibilidade**
- Python (pandas, numpy, scipy, statsmodels, matplotlib/seaborn), a menos que o
  estudante decida outro.
- Semente aleatória fixa. O notebook deve rodar **do início ao fim** sem intervenção.
- Código limpo, comentado em português, organizado nas mesmas etapas do relatório (I a IV).
- Salve figuras e tabelas em `outputs/` com nomes descritivos.
- Mantenha `requirements.txt` e um `README.md` com instruções de execução.

**Comunicação**
- Ao concluir cada etapa, resuma em poucas linhas: o que foi feito, o que foi
  encontrado e o que vem a seguir.
- Aponte riscos e dúvidas (ex.: coluna suspeita, variável ambígua) em vez de supor.
- O estudante é o autor: explique de modo que ele **entenda e consiga defender** cada
  escolha. Não entregue conclusões prontas sem o raciocínio.

## 9. Registro de Progresso (atualize a cada sessão)

**Estado atual:** Projeto 100% finalizado e validado rigorosamente. Todas as 8 demandas de finalização concluídas: gráfico de dispersão com jitter e tendência linear adicionado ao notebook e PDF; correção de redação de P2 ("probabilidade de superioridade de aproximadamente 77%, contando empates pela metade"); fonte Unicode DejaVu Sans registrada no ReportLab com todos os glifos matemáticos validados; caminhos 100% relativos; `.gitignore` e análise de licença Apache 2.0 do Kaggle consolidados; espaço reservado para repositório do GitHub destacado no PDF e README; reexecução limpa do notebook `analise_depressao.ipynb` com todas as saídas salvas; e inspeção visual página a página do PDF `relatorio_executivo_bi.pdf` (8 páginas perfeitas, resumo executivo em 1 página).

**Checklist**
- [x] Dataset escolhido
- [x] Requisitos conferidos no CSV real (500+ linhas, 5+ numéricas, 3+ categóricas)
- [x] Etapa I: objetivo geral e 3 a 5 perguntas de negócio
- [x] Etapa II: limpeza e tipagem
- [x] Etapa II: descritiva univariada (numéricas e categóricas)
- [x] Etapa II: bivariada, gráficos e matriz de correlação
- [x] Etapa III: intervalo(s) de confiança
- [x] Etapa III: testes de hipóteses (pressupostos, estatística, p-valor, efeito, decisão)
- [x] Etapa IV: recomendações e plano de ação
- [x] Relatório PDF completo (resumo executivo de até 1 página na capa, fonte Unicode DejaVu Sans, 8 páginas)
- [x] Notebook rodando do início ao fim a partir da raiz com caminhos relativos
- [x] Gráfico de dispersão Study Satisfaction × CGPA (P5) adicionado ao notebook e PDF
- [x] Correção de redação P2 (probabilidade de superioridade de ~77%, contando empates pela metade)
- [x] Símbolos matemáticos (α, χ², ρ, ≈, ±, ≤, ≠) renderizados com suporte Unicode nativo
- [x] .gitignore criado e licença Apache 2.0 verificada no Kaggle
- [x] Espaço do link do GitHub destacado no PDF e no README

**Log**

| Data | O que foi feito | Próximos passos |
|---|---|---|
| 2026-10-12 | Roteiro analisado; tema de saúde mental definido; candidatos de dataset levantados | Escolher o dataset e formular as perguntas de negócio |
| 2026-10-12 | Dataset escolhido: Student Depression Dataset (Kaggle) | Baixar o CSV para `data/`, inspecionar colunas e tipos, conferir requisitos e fechar as perguntas |
| 2026-10-12 | Inspeção completa do CSV em `data/` (27.901 linhas, 18 colunas, 0 duplicatas, 3 nulos em Financial Stress); requisitos atendidos; 5 perguntas de negócio propostas com testes estatísticos e justificativas | Obter aprovação do estudante para fechar a Etapa I e iniciar a Etapa II (limpeza e descritiva) |
| 2026-10-12 | Etapa II concluída: limpeza (N=27.837 após exclusão de 64 linhas justificadas); análise de outliers de Age e Horas; sensibilidade do CGPA; tabelas univariadas e bivariadas geradas; 5 figuras salvas em `outputs/` | Iniciar Etapa III: Intervalos de Confiança e Testes de Hipóteses com verificação formal de pressupostos e cálculo de tamanhos de efeito |
| 2026-10-12 | Etapa III concluída: IC 95% de Wilson para depressão [57,94%, 59,10%]; Mann-Whitney U (U=1,45e8, p<0,001, r_rb=0,54) e Welch (t=89,2, d=1,10); Qui-Quadrado sono (chi2=277,9, V=0,10); Qui-Quadrado finança (chi2=3695,0, V=0,36) com Cochran-Armitage (Z=60,67, p<0,001); Spearman satisfação x CGPA (rho=-0,047, efeito negligenciável); controle Holm-Bonferroni; notebook reprodutivo `analise_depressao.ipynb` e `README.md` consolidados | Iniciar Etapa IV: Redação do Relatório Executivo em PDF e estruturação das recomendações de BI |
| 2026-10-12 | Etapa IV concluída: Relatório Executivo em PDF gerado (`relatorio_executivo_bi.pdf`, 7 seções, capa com resumo executivo de exatamente 1 página, tabelas e figuras em alta resolução); notebook `analise_depressao.ipynb` reexecutado com saídas salvas e ajustes textuais (probabilidade de superioridade de 77%, 4 famílias de hipóteses, H0/H1 explícitas, suposições metodológicas); `README.md` e `requirements.txt` atualizados | Realizar os 8 itens de finalização e polimento final |
| 2026-10-12 | Finalização Completa: (1) Gráfico de dispersão P5 com jitter e reta linear adicionado ao notebook e PDF; (2) Redação de P2 corrigida para probabilidade de superioridade de ~77% contando empates pela metade; (3) Fonte Unicode DejaVu Sans registrada no ReportLab sanando todos os símbolos; (4) Todos os caminhos convertidos para relativos; (5) .gitignore criado e licença Apache 2.0 confirmada no Kaggle; (6) Placeholder do GitHub destacado no PDF e README; (7) Reexecução limpa de ponta a ponta do notebook com saídas gravadas; (8) PDF inspecionado visualmente página a página via PyMuPDF (resumo em 1 página, sem cortes, paginação 1-8). | Entrega final pelo estudante (inserir link do repositório no GitHub e submeter arquivos) |

## 10. Perguntas de negócio e procedimentos estatísticos finalizados

| # | Pergunta de Negócio (BI Universitário) | Variáveis Envolvidas | Procedimento Estatístico Principal | Procedimento Confirmatório / Tamanho de Efeito | Justificativa Metodológica |
|---|---|---|---|---|---|
| 1 | Qual é a proporção estimada de estudantes com indicativo de depressão na população-alvo da pesquisa? | `Depression` (binária: 0/1) | Intervalo de Confiança de 95% de Wilson | Limites: [57,94%, 59,10%] (p = 58,52%) | Método de Wilson score é recomendado para proporções binomiais mesmo em amostras grandes, evitando aproximações impróprias nos extremos. Interpretação restrita à população amostrada (não probabilística). |
| 2 | O nível de pressão acadêmica percebida difere significativamente entre estudantes com e sem indicativo de depressão? | `Academic Pressure` (escala 0-5) × `Depression` (binária) | Teste U de Mann-Whitney ($U = 1,45 \times 10^8$, $p < 0,0001$) | Teste t de Welch ($t = 89,21$, $p < 0,0001$) + Correlação Bisserial por Postos ($r_{rb} = 0,5408$) + $d$ de Cohen ($1,0950$) | Mann-Whitney é o procedimento prioritário por se tratar de escala discreta/ordinal (0 a 5). Teste t de Welch entra como suporte paramétrico assintótico. Efeito substantivo e de grande magnitude. |
| 3 | A duração habitual do sono está associada à ocorrência de indicativo de depressão entre os estudantes? | `Sleep Duration` (4 faixas) × `Depression` (binária) | Teste Qui-Quadrado de Independência ($\chi^2 = 277,90$, $p < 0,0001$, $gl=3$) | $V$ de Cramér ($V = 0,0999$) + Proporção de depressão por faixa | Ambas são categóricas. Em $N=27.837$, o $\chi^2$ rejeita a independência, mas o $V$ de Cramér quantifica uma associação fraca ($V \approx 0,10$). Relação não-monotônica descrita sem teste de tendência. |
| 4 | A prevalência de depressão varia e exibe tendência monotônica crescente em função do estresse financeiro? | `Financial Stress` (escala 1 a 5) × `Depression` (binária) | Teste Qui-Quadrado de Independência ($\chi^2 = 3695,04$, $p < 0,0001$, $gl=4$) | Teste de Tendência de Cochran-Armitage ($Z = 60,67$, $p < 0,0001$) + $V$ de Cramér ($V = 0,3643$) | Avalia associação e gradiente monotônico estrito entre vulnerabilidade socioeconômica e depressão (a taxa sobe de 31,8% no nível 1 para 81,2% no nível 5 com efeito moderado a forte). |
| 5 | Existe correlação entre a satisfação do estudante com os estudos (`Study Satisfaction`) e o seu rendimento acadêmico (`CGPA`)? | `Study Satisfaction` (escala 0-5) × `CGPA` (contínua) | Coeficiente de Correlação de Spearman ($\rho = -0,0467$, $p < 0,0001$) | Correlação de Pearson ($r = -0,0466$, $p < 0,0001$) | `Study Satisfaction` afere a percepção subjetiva com os estudos; Spearman avalia monotonicidade de forma não paramétrica. Embora estatisticamente significante pelo $N$, a magnitude de $\rho$ é desprezível ($|\rho| < 0,10$). |
