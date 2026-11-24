# Leia-me: o que é este projeto e o que foi feito até agora

*Última atualização: 23/11/2026. Siglas em [00_GLOSSARIO.md](00_GLOSSARIO.md). Resultados completos em [RESULTADOS_VALIDACAO.md](RESULTADOS_VALIDACAO.md).*

Esta pasta é uma **cópia de testes**. O projeto principal está no repositório git privado
(`Modelo_cardiovascular_PBL_Felipe`). Aqui testamos melhorias antes de levá-las para lá.

---

## 1. O projeto em uma página

**O problema clínico.** No choque vasodilatador (geralmente por sepse), os vasos se dilatam e a pressão
arterial cai. O tratamento é a **noradrenalina**, que contrai os vasos. Quando nem doses altas resolvem
(choque **refratário**), pode-se acrescentar a **angiotensina II**. Idosos respondem diferente, porque as
artérias deles são mais rígidas, e quem usa remédios de pressão do tipo BRA/IECA responde menos à Ang II.

**O modelo.** Um programa em Julia simula a circulação com um **Windkessel de 3 elementos** (modelo 0D):
o coração empurra sangue para um "balão elástico" (as artérias, com complacência **C**) que escoa por uma
"torneira" (os vasos pequenos, com resistência **R_p**). O choque é representado por R_p baixa. Os
remédios agem fechando a torneira (sobem R_p), com uma curva dose-efeito (Hill) e um atraso (meia-vida).
O idoso tem R_p × 1,15 e C × 0,79 (era 0,5; ver a seção 6). Os parâmetros vêm da **literatura**, não de
pacientes reais. Um aplicativo (GLMakie) mostra as simulações em 6 abas.

**A pergunta desta etapa.** O modelo descreve pacientes **reais**? Para responder, usamos o **MIMIC-IV**:
dados de dezenas de milhares de internações em UTI (Boston), com pressão, frequência cardíaca e doses
de remédio minuto a minuto.

**Resposta curta, por enquanto.** O modelo é um **simulador didático de uma hipótese** (a resposta aos
vasopressores satura, e mais ainda no refratário). A pressão antes do tratamento fica numa faixa plausível
e o efeito pequeno de cada aumento de noradrenalina é compatível com os dados. Mas o modelo **não prevê**
a PAM de cada paciente, subestima a PAM da população já tratada e não acerta a forma do pulso (PAD).
Detalhes nas seções 5 e 6; perguntas e respostas na seção 7.

## 2. O que tem na pasta

```
Modelagem Windkessel/
├── README.md                         ← este arquivo
├── 00_GLOSSARIO.md                   ← siglas e termos
├── RESULTADOS_VALIDACAO.md           ← documento completo de resultados (base para o relatório)
├── Metodologia de validação ... .docx  ← o plano de validação (5 níveis), escrito com 33 pacientes
├── PBLMODELAGEMCSV.ipynb             ← notebook Python: extrai os pacientes e faz as análises (seções 1 a 15)
├── preparar_mimic.py                 ← converte o MIMIC para Parquet (rodar uma vez)
├── mimic completo/
│   ├── *.csv.gz                      ← dados originais do MIMIC-IV (NÃO abrir no Excel: são enormes)
│   ├── parquet/                      ← versão compacta e rápida, criada pelo preparar_mimic.py
│   ├── validacao/                    ← resultados da coorte "todos" (8.276 internações) + figuras/
│   ├── validacao_vasodilatador/      ← resultados da coorte "vasodilatador" (2.909 internações) + figuras/
│   └── angiotensina/                 ← seção 15: casos com Ang II × controles + figuras/
└── Modelo_cardiovascular_PBL_Felipe-correcoes-revisao/.../
    ├── modelo.jl                     ← o modelo (equações e parâmetros)
    ├── app_abas.jl e aba_*.jl        ← o aplicativo (6 abas)
    ├── aba_mimic.jl                  ← aba 6 · Validação do modelo: tabela-resumo + gráficos × MIMIC (novo)
    ├── resumo_mimic.jl               ← gera dados_mimic/, os resumos agregados da aba 6 (novo)
    ├── dados_mimic/                  ← resumos agregados (fora do git: ver .gitignore)
    ├── verificar.jl                  ← nível 0: o código resolve as equações certas?
    ├── validar.jl                    ← níveis 1, 2 e 3 contra o MIMIC (novo)
    ├── planta_individual.jl          ← o modelo recebendo FC/DC de cada paciente (novo)
    └── valida.jl                     ← script antigo da 1ª passada (lê a planilha; não usar)
```

## 3. Como rodar

### Só abrir o app (os dados já estão prontos)

1. No VS Code: **File → Open Folder…** e escolha `Modelagem Windkessel`. Abra um terminal (`` Ctrl+` ``).
2. `cd ".\Modelo_cardiovascular_PBL_Felipe-correcoes-revisao\Modelo_cardiovascular_PBL_Felipe-correcoes-revisao"`
3. `julia app_abas.jl`. Na primeira vez a janela demora até 1 min (o GLMakie compila). Use `julia` sem
   `--project=.`, porque o GLMakie está no ambiente global do Julia.

### Refazer tudo do zero (cerca de 10 minutos)

Precisa do ambiente Python `eng_biomedica` (já tem duckdb, pandas, pyarrow e matplotlib) e do Julia.

1. **Converter o MIMIC** (só na primeira vez; cerca de 2,5 min). Na pasta `Modelagem Windkessel`:
   `& "C:\Users\arthu\miniconda3\envs\eng_biomedica\python.exe" preparar_mimic.py "mimic completo"`
2. **Notebook, seções 1 a 12b** (cerca de 1 min): abrir `PBLMODELAGEMCSV.ipynb`, escolher o kernel
   `eng_biomedica` (**Select Kernel → Python Environments**) e rodar até a seção **12b**. Na seção 12,
   `COORTE = "vasodilatador"` ou `"todos"` escolhe a coorte (cada uma vai para uma pasta própria).
3. **Validação** (segundos). Na pasta do repositório:
   `julia validar.jl "..\..\mimic completo\validacao_vasodilatador"`
   `julia planta_individual.jl "..\..\mimic completo\validacao_vasodilatador"`
4. **Notebook, seções 13 a 15**: concordância/Bland-Altman (13), diferença em diferenças (14; de 1 a 5 min) e Ang II × controles (15; cerca de 2 min).
5. **App com a aba de validação**: `julia resumo_mimic.jl` (5 s; usa as duas pastas de validação e as seções 14 e 15) e
   `julia app_abas.jl`.

| Mensagem de erro | O que fazer |
|---|---|
| `julia não é reconhecido` | Feche e abra o VS Code; se continuar, reinstale o Julia pelo juliaup. |
| `Package GLMakie not found` | Rode sem `--project=.`. |
| O notebook não acha `duckdb` | Kernel errado: escolha `eng_biomedica`. |
| `Pasta ... não existe` no `validar.jl` | Rode antes a seção 12 do notebook para essa coorte. |
| Aba 6 diz "Sem dados do MIMIC" | Rode `julia resumo_mimic.jl`. |

## 4. O que foi feito, em ordem

1. **1ª passada (antes desta pasta):** 33 internações do MIMIC *demo*, pequeno demais para concluir
   qualquer coisa (19 pacientes com PAM antes da nora). Ver o documento .docx.
2. **Arquivos que faltavam:** o `chartevents` (todas as pressões), o `validar.jl` (o `valida.jl` que existia
   lia a planilha antiga e um caminho do computador do Bruno) e o `preparar_mimic.py`.
3. **Eficiência:** os arquivos completos têm até 30 GB descompactados. Com o DuckDB, convertemos tudo
   para Parquet guardando só as linhas úteis (o chartevents foi de 2,5 GB para 71 MB). O notebook foi
   ajustado para milhares de pacientes: passou de horas para cerca de 1 minuto.
4. **`validar.jl` novo:** níveis 1 a 3 do documento, com validação cruzada por paciente em 5 partes.
5. **Planta com entradas reais (`planta_individual.jl`):** o modelo recebe a FC e o DC de cada paciente,
   e também é rodado "ao contrário" para calcular que R_p e C cada paciente teria.
6. **Filtro de choque vasodilatador:** sepse, sem choque cardiogênico ou hipovolêmico, fora das UTIs
   cardíacas. Serviu para testar se os erros vinham de pacientes que o modelo não pretende representar.
7. **C do idoso recalibrado para 0,79** e **aba 6 · Validação do modelo** no app (tabela-resumo fixa à esquerda, gráficos que seguem os sliders).
8. **Gráficos refeitos** (densidade em vez de nuvem de pontos; PAM > 180 removida como artefato).
9. **Diferença em diferenças (seção 14):** o teste mais direto do que o modelo afirma sobre a noradrenalina.

## 5. Resultados principais (coorte vasodilatador, salvo indicação)

| Nível | Pergunta | Resultado |
|---|---|---|
| 0 | O código resolve as equações? | ✓ Passa (`verificar.jl`). Com C × 0,79, o cenário do idoso não bate mais com o documento antigo (esperado). |
| 1 | A pressão do modelo antes da nora é realista? | **PAM ~** (modelo 58/62 contra medianas 63/64; dentro do IIQ, mas o IIQ é largo). **PAD ✗**: cerca de 15 mmHg abaixo no adulto e 13 no idoso. **PP do idoso**: 51 com C × 0,79 (era 74), contra 42 medidos (IIQ 33–55). |
| 2 | O modelo prevê a PAM de cada paciente depois da nora? | ✗ Não ganha da "média da população" (RMSE 16,5 contra 13,2 mmHg; CCC de Lin 0,21 e −0,01). O modelo subestima a PAM da população tratada em cerca de 10 mmHg. |
| 2b | Cada aumento de nora sobe a PAM quanto? (diferença em diferenças) | ✓ **Compatível**: +0,6 mmHg (IC 95% −0,4 a +1,7) nos dados e +0,25 no modelo. Atenção: o +0,25 não é uma previsão livre, vem de premissas do grupo (ver seção 7). |
| 3 | No refratário, nora ≥ 0,2 deixa a PAM abaixo de 65? | ✗ Só 42% das medidas (41% antes do filtro de PAM > 180) (o critério pedia > 50%). A equipe sobe a dose até chegar a 65. |
| 3b | O refratário deixa de responder ao aumento de dose? | ~ **Coerente com a teoria**: refratário +0,2 (IC −1,4 a +1,8), não refratário +1,7 (IC +0,4 a +3,1), dose já ≥ 0,2: −3,2 (IC −7,9 a +0,6). |
| 4 | A Ang II simulada se parece com o ATHOS-3? | Coorte virtual: ainda não feita. |
| 4b | A Ang II real (MIMIC) responde como o modelo prevê? | ✗ / inconclusivo. Com 21 casos pareados, o efeito real foi +9 pontos percentuais de respondedores (IC −13 a +31) e −1,4 mmHg de PAM (IC −7 a +4). O modelo prevê 67% de respondedores e +11 mmHg. Ver "Angiotensina II no MIMIC" abaixo. |

### Diferença em diferenças (seção 14), em detalhe

Cada aumento de dose (≥ 20%) é comparado com **períodos de dose estável que partem da mesma PAM**
(faixas de 5 mmHg) **e da mesma faixa de dose**. Nos dois casos mede-se a variação da PAM entre os 30 min
antes e os 15 a 45 min depois.

- **A PAM baixa sobe sozinha** (gráfico da esquerda): partindo de 50 mmHg, ela sobe cerca de 15 mmHg
  *com ou sem* aumento de dose. Por isso os "+5 mmHg depois do aumento" que medimos antes eram, em
  quase tudo, **regressão à média**, e não efeito da noradrenalina.
- **Descontada a regressão à média** (gráfico da direita):

| Recorte (coorte vasodilatador) | Efeito do aumento (IC 95%) | Modelo |
|---|---|---|
| Todos (760 aumentos) | +0,6 (−0,4 a +1,7) | +0,25 |
| Dose < 0,2 | +1,1 (0,0 a +2,2) | +0,25 |
| Dose já ≥ 0,2 | −3,2 (−7,9 a +0,6) | +0,22 |
| Refratário (≥ 6 h com dose ≥ 0,2) | +0,2 (−1,4 a +1,8) | +0,25 |
| Não refratário | **+1,7 (+0,4 a +3,1)** | +0,24 |
| Refratário (precisou de 2º vasopressor) | +0,5 (−1,1 a +1,8) | +0,25 |

  Na coorte "todos" (que inclui choque cardiogênico e pós-cirurgia cardíaca), o efeito é maior e claro:
  +2,1 (IC +1,4 a +2,7), e o modelo (+0,26) fica abaixo do intervalo.

- **Leitura:** no choque vasodilatador, aumentar a noradrenalina sobe pouco a PAM, e no refratário ou com
  dose já alta o efeito é indistinguível de zero. Isso é **coerente com a teoria e com o modelo**. O modelo
  subestima o efeito nos não refratários, porque ele só representa o estado refratário.
- **Limites:** o pareamento é pelo nível da PAM, não pela tendência. Se a equipe aumenta a dose quando
  a PAM *está caindo*, o efeito real é maior que o medido. Além disso, os aumentos são pequenos (mediana de
  +0,05 µg/kg/min; metade entre +0,03 e +0,10) e a PAM não invasiva é medida a cada 15 a 60 min.

### Angiotensina II no MIMIC: casos × controles pareados (seção 15 do notebook)

**Desenho.** Os casos são as internações que receberam Ang II, com t = 0 no início dela. Os controles
funcionam como um "placebo do mundo real": internações que **nunca** receberam Ang II, num instante em que a
noradrenalina estava ≥ 0,4 µg/kg/min. Cada caso foi pareado com até 5 controles de PAM basal (±5 mmHg),
dose de noradrenalina (±0,15) e status de sepse parecidos. O desfecho é o do ATHOS-3: na hora 3 (média de
150 a 210 min), PAM ≥ 75 **ou** subida ≥ 10 mmHg, **sem** aumento dos outros vasopressores. O modelo
(modo "nora fixa + Ang II", com Emax de 0,5 e r = 1) recebe a PAM basal e as **doses reais** de Ang II de cada caso.

**Quem entrou:** 29 internações com Ang II. Saíram 2 sem PAM basal, 6 sem PAM na hora 3 e 1 sem dose válida
de noradrenalina, sobrando 22. Destas, 21 tiveram controle pareado (mediana de 5 controles, de 2.547 possíveis).
Um registro de dose foi excluído (405 ng/kg/min, implausível). Doses em µg/kg/min foram convertidas (× 1000).

| Fonte | Responderam com Ang II | Controle / placebo | Efeito (pontos percentuais) |
|---|---|---|---|
| ATHOS-3 (ensaio randomizado, 163 × 158) | 69,9% | 23,4% | **+46,5** (IC 36,9 a 56,2) |
| MIMIC pareado (21 casos) | 33% | 25% | **+8,6** (IC −13 a +31) |
| MIMIC, só PAM basal 55–70 como no ATHOS-3 (13 casos) | 23% | 14% | +9,2 (IC −17 a +39) |
| Modelo, Emax 0,5 (doses reais) | 67% | 0% (o modelo não tem placebo) | +67 (faixa de 62 a 67 com Emax 0,3 a 1,0) |
| Modelo, se todos usassem BRA (r = 11,9) | 19% | 0% | +19 |

- **Variação da PAM em 3 h:** casos +3,4, controles +4,8, ou seja, efeito de **−1,4 mmHg** (IC −6,9 a +4,4).
  O modelo prevê **+11,1 mmHg**.
- **Dose de noradrenalina em 3 h:** os casos reduziram −0,06 e os controles −0,18 µg/kg/min. A Ang II **não**
  permitiu reduzir mais a noradrenalina que nos controles. Pelo contrário: os controles melhoraram mais.
  Mesmo assim, a nora caiu em 8 dos 21 casos, o comportamento do modo "troca".

**Leitura.**
1. O modelo reproduz o **braço Ang II do ATHOS-3** (67% contra 69,9%), o que era esperado, porque foi
   calibrado com ele. Isso **não** é uma validação independente.
2. Nos pacientes reais do MIMIC, o efeito da Ang II foi **bem menor** que no ensaio e no modelo, e o intervalo
   do MIMIC nem cruza o do ATHOS-3. Mas o resultado é **inconclusivo** por causa dos cuidados abaixo,
   principalmente o n mínimo e a gravidade maior dos casos.
3. O dado da noradrenalina sugere que os casos eram pacientes **piorando** (por isso receberam Ang II),
   enquanto os controles com a mesma dose estavam em recuperação. O pareamento pelo nível não captura a
   tendência, e isso puxa o efeito para baixo.

**Cuidados e limitações (todos precisam constar no relatório):**
1. **n mínimo**: 21 casos, resultado ilustrativo. Os intervalos de confiança são enormes.
2. **PAM esparsa**: em cada janela pode haver só 1 ou 2 medidas.
3. **Não é randomizado**: a Ang II é dada como resgate a pacientes escolhidos pela equipe. O pareamento por
   PAM, noradrenalina e sepse reduz a confusão, mas **não pareia a tendência** (piorando × melhorando),
   nem lactato, volume, corticoide ou outros vasopressores em dose.
4. **Regressão à média**: descontada pelo controle pareado pela PAM basal; sem isso, o efeito pareceria maior.
5. **Sem dado de BRA/IECA crônico**: o fator r, a principal conclusão do modelo, **não é testável** aqui. A linha
   "todos com BRA" só mostra o limite inferior do modelo.
6. **Unidades misturadas** (ng/kg/min e µg/kg/min) e um registro implausível excluído.
7. **O modelo assume noradrenalina fixa**; na vida real ela mudou em parte dos casos.
8. **Calibração × validação**: a Ang II do modelo foi calibrada com subgrupos do próprio ATHOS-3; comparar
   com o ATHOS-3 é circular. A comparação com o MIMIC é externa, mas com n mínimo.
9. **O modelo não tem placebo**: sem Ang II, a PAM dele não muda (0%). A comparação justa é a do **efeito**
   (diferença entre os braços), não a % de respondedores.
10. **Critério de entrada diferente**: o ATHOS-3 exigia PAM basal entre 55 e 70. Vários casos do MIMIC já
    estavam acima de 70 (daí o recorte 55–70).
11. **Meta clínica diferente**: o ATHOS-3 titulava até 75; na rotina a meta costuma ser 65, e a Ang II pode
    ser usada para reduzir a noradrenalina, e não para subir a PAM.
12. Um único centro; a Ang II só aparece nos anos mais recentes do MIMIC (aprovada no fim de 2017).

Os arquivos ficam em `mimic completo/angiotensina/`: `casos.csv` (dados por paciente: **não compartilhar**),
`resumo.csv` e as figuras `resposta_athos.png` e `casos_individuais.png` (cada caso com a PAM medida e a prevista).

### Planta com entradas reais

- Usar a FC do próprio paciente **não melhora** o modelo.
- O DC medido (raro: 126 internações, 82% de cirurgia cardíaca) fica em 4 a 5 L/min, contra 10 L/min no
  modelo, calibrado para sepse hiperdinâmica (Melo & Peters 1999). Entre os sépticos só 11 têm DC medido,
  então não dá para confirmar nem descartar esse valor.
- Calculando R_p e C a partir dos dados, o idoso tem R_p de 1,1 a 1,35 vez o do adulto (modelo: 1,15,
  coerente) e C de 0,75 a 0,9 vez (modelo antigo: 0,5). Daí a escolha de 0,79.

### Como ler os gráficos de concordância (seção 13)

- **Prevista × medida (em cima):** quanto mais escuro o hexágono, mais medidas caem ali. Se o modelo
  acertasse, tudo ficaria na diagonal tracejada. A linha vermelha é a mediana da previsão em cada faixa de
  PAM medida: se fica "deitada", o modelo não acompanha as variações reais.
- **CCC de Lin:** de −1 a 1. Vale 1 com previsão idêntica à medida e 0 sem concordância. Abaixo de 0,90 a
  concordância é ruim. Aqui: 0,21 (modelo A, igual à referência "PAM fica igual") e −0,01 (modelo B).
- **Bland-Altman (embaixo):** erro (prevista − medida) contra o nível de pressão. A linha cheia é o viés;
  as tracejadas são os limites de 95%. Limites de ±40 mmHg são largos demais para uso clínico. A curva
  laranja mostra se o erro depende do nível de pressão.
- **A faixa diagonal do modelo B não é defeito do gráfico:** um preditor que dá sempre o mesmo número
  (62 mmHg) gera erros sobre uma reta inclinada.

## 6. Conclusões

- **PAM: só parcialmente.** *Antes* da nora, a PAM do modelo cai dentro do IIQ real (critério fraco,
  porque o IIQ vai de cerca de 56 a 74). *Depois* da nora, a média real sobe para 70 a 72 e o modelo fica
  entre 59 e 63: ele **subestima a PAM da população tratada em cerca de 10 mmHg**. Pela seção 14, essa subida
  real vem quase toda de recuperação espontânea e de outros fatores (volume, tratamento da infecção), que
  o modelo não tem, e não da noradrenalina.
- **Forma do pulso (PAS, PAD, PP).** São dois erros diferentes:
  1. **Fator de idade da complacência forte demais.** Com C × 0,5, a PP do idoso saía 74; os dados indicam
     de 0,8 a 1,0. O grupo escolheu **0,79**, que dá PP 51 (era 74; medida: 42). Faz sentido: o 0,5 vem de
     idosos saudáveis em pressão normal; no choque, com pressão baixa, as artérias de qualquer idade ficam
     mais complacentes e a diferença entre idoso e adulto diminui.
  2. **A PAD não se corrige com C.** Nos pacientes, a PAM fica a cerca de 1/3 do caminho entre a PAD e a PAS;
     no modelo, perto da metade. É um erro de **forma da onda** (ejeção em meia senoide, sem reflexão de
     onda no Windkessel de 3 elementos). Seria preciso mudar Q_in ou usar um Windkessel de 4 elementos.
- **Efeito da noradrenalina:** a previsão medida a medida (nível 2) não consegue medi-lo, por causa do
  viés de indicação. A diferença em diferenças consegue: o efeito de cada aumento é pequeno, quase nulo no
  refratário e com dose alta, e é compatível com o do modelo.
- **Refratário:** no modelo, a falta de resposta é **imposta** (critério 4), não um resultado. Os dados,
  depois de descontada a regressão à média, **apoiam** essa premissa no choque vasodilatador. O critério 4
  ao pé da letra ("não chega a 65") não se sustenta, porque a equipe titula até 65 e acrescenta outros
  vasopressores.
- **O modelo se justifica?** Como **ferramenta didática e mecanística** da hipótese do choque refratário,
  sim: a premissa central (resposta pequena e saturada à noradrenalina) tem apoio nos dados. Como
  **preditor clínico** de cada paciente, não.

## 7. Perguntas discutidas (e respostas)

**Os arquivos do MIMIC são enormes e nem abrem. Como trabalhar com eles?**
Nunca abrir no Excel. O DuckDB lê o `.csv.gz` direto, sem carregar tudo na memória, e converte uma vez
para Parquet guardando só as linhas úteis (`preparar_mimic.py`). Depois disso, tudo roda em segundos.

**O que faltava na pasta original?**
O `chartevents.csv.gz` (sem ele não há pressão), o `validar.jl` (o `valida.jl` existente é da 1ª passada e
não lê o que o notebook exporta) e o `preparar_mimic.py` citado no notebook.

**A validação comparou o modelo "sintético" com os dados reais?**
Em parte. No nível 1, sim: o modelo, só com parâmetros da literatura, contra a pressão real. No nível 2, o
modelo já recebia a dose real de cada paciente e a PAM inicial dele. Depois a planta passou a receber
também a FC e o DC de cada paciente (`planta_individual.jl`).

**O que é o nível 4 (angiotensina II)?**
A Ang II foi calibrada com subgrupos do ATHOS-3. A validação honesta usa um desfecho que não entrou na
calibração: montar uma coorte virtual (centenas de pacientes sorteados), rodar o protocolo do ensaio
(`titular`) e comparar a % de "respondedores" na hora 3 (PAM +10 ou ≥ 75) com os 69,9% do ATHOS-3
(23,4% no placebo). O MIMIC completo também tem 29 internações reais com Ang II para uma checagem
descritiva. Ainda não foi feito.

**Filtrar só choque vasodilatador mudou alguma coisa?**
Quase nada nos níveis 1 a 3, o que mostra que os erros vêm do modelo e não da mistura de pacientes. Na
diferença em diferenças fez diferença: na coorte "todos" a noradrenalina tem efeito claro (+2,1 mmHg por
aumento); no choque vasodilatador o efeito é pequeno ou nulo, como a teoria prevê.

**O modelo está mal calibrado? O fator de idade é drástico demais?**
O fator de complacência do idoso (0,5) era drástico demais: os dados apontam de 0,75 a 0,9, e o grupo
adotou 0,79. A PAD baixa vem da forma da onda e não se resolve com C. É o limite de um modelo 0D, que o
grupo já conhecia.

**Uma aba com comparação em tempo real com o MIMIC é válida?**
Sim, com cuidados. "Tempo real" quer dizer que a aba reage aos sliders; os dados reais são resumos fixos.
Ajustar sliders até as curvas coincidirem é **calibração a olho**, não validação, e por isso a aba mostra
ao lado o placar fixo da validação cruzada. Só entram resumos agregados (≥ 11 pacientes por valor), e
mesmo assim o termo de uso do PhysioNet vale: `dados_mimic/` está no `.gitignore` até o grupo decidir.

**Por que os gráficos estavam "grotescos"?**
Excesso de dados (10 a 27 mil pontos sobrepostos virando uma mancha), valores absurdos de PAM (até
300 mmHg, artefatos) que esticavam os eixos, e médias com grupos de poucos pacientes. Agora há mapas de
densidade, PAM > 180 é descartada e cada ponto exige pelo menos 10 pacientes.

**CCC de Lin e Bland-Altman são a melhor análise para este modelo?**
Não. Eles testam se o modelo prevê cada medida de cada paciente, e o modelo não foi feito para isso (ele
representa um paciente típico, e os dados são observacionais). O teste adequado é o do que o modelo
afirma: a resposta a cada aumento de dose, descontada a regressão à média (seção 14). Os dois gráficos
continuam no notebook como registro do nível 2 do documento.

**"A PAM está realista", mas os gráficos mostram o contrário?**
A afirmação era exagerada e foi corrigida. Ela valia só para a PAM *antes* da noradrenalina, e com um
critério fraco (dentro do IIQ). *Depois* da noradrenalina, o modelo subestima a PAM da população em cerca
de 10 mmHg, e na previsão de cada paciente não concorda (CCC 0,21).

**No refratário, a noradrenalina não deveria alterar a PAM? Os dados e o modelo mostram isso?**
O modelo mostra, mas porque a falta de resposta foi imposta (critério 4), e ele não tem um estado "não
refratário" para comparar. Nos dados, a comparação ingênua sugeria +5 mmHg em todos. Descontada a
regressão à média, o efeito no refratário é ≈ 0 (+0,2; IC −1,4 a +1,8), com dose já alta é ≈ 0 ou negativo,
e só nos não refratários é claramente positivo (+1,7). Ou seja, **os dados apoiam a teoria**, com os
limites descritos na seção 5.

**De onde vem o "+0,25 mmHg" do modelo? Foi pré-estabelecido?**
Sim, em boa parte. No modelo, o efeito da noradrenalina é uma curva de Hill sobre R_p:
E = Emax_NE · dose / (EC50 + dose), com:

| Parâmetro | Valor | Origem |
|---|---|---|
| Emax_NE | 0,5 × (65 / PAM_choque − 1) | **Premissa do grupo**: o "teto" vem do critério 4 (a nora sozinha não pode levar a PAM a 65), e o 0,5 é a fração desse teto (`NE_FRAC`, slider da aba 2). `teto_ne` em `modelo.jl:185`. |
| EC50 | 0,2 µg/kg/min | **Premissa do grupo**: reaproveita o limiar de "dose alta" do ATHOS-3 (`DOSE_NE_ALTA`). |
| t½ | 6,8 min no app (4,4 na validação) | **Literatura**: faixa de 2 a 6,8 min (Beloeil 2005). |

Com isso, o efeito máximo possível da nora é +3,5 mmHg no adulto e +1,4 no idoso, e um aumento típico
(+0,05 µg/kg/min) dá +0,3 e +0,1 mmHg. O +0,25 é a média dos aumentos reais nesta fórmula. Ou seja, o
modelo não *prevê* que a resposta é pequena: ele foi construído para que ela seja pequena (estado refratário
imposto). O que a seção 14 mostra é que **essa premissa é compatível com os dados**, não que o modelo a
descobriu. O relatório (seção 2.4) descreve a farmacodinâmica só da Ang II; a da nora precisa ser descrita
como premissa.

**O modelo prevê diferença entre adulto e idoso na resposta à nora?**
Prevê: cerca de 2,5 vezes mais efeito no adulto (+0,36 contra +0,15 por aumento). Mas essa diferença **não
vem de nenhuma farmacologia do envelhecimento**. Ela vem só da regra do teto: o idoso em choque tem PAM mais
alta (62 contra 58), então sobra menos "espaço" até 65 e o Emax dele fica menor. É um efeito colateral da
forma como o critério 4 foi escrito.

**Como medir a diferença entre adultos e idosos nos dados?**
Três formas, da mais simples à mais forte:
1. **Antes do tratamento** (mediana por grupo, coorte vasodilatador): PAM 63 × 64, PP 40 × 42, PAD 52,5 × 52.
   Na prática não há diferença. O modelo prevê PAM 58 × 62 e PP 44 × 51, ou seja, mais diferença entre as
   idades do que os pacientes mostram. A proporção de refratários também é parecida (37% × 32%).
2. **Na resposta a cada aumento de dose** (diferença em diferenças separada por grupo, com a diferença
   adulto − idoso e IC por bootstrap de pacientes): adulto +1,1 (IC −0,5 a +2,8), idoso +0,6 (IC −0,6 a +1,9).
   **Diferença: +0,5 mmHg (IC 95% −1,6 a +2,5)**, ou seja, não detectável. Normalizando pelo tamanho do
   aumento (+0,1 µg/kg/min), os intervalos ficam ainda mais largos.
3. **Idade contínua, por faixa** (18–49, 50–64, 65–74, 75–84, ≥ 85): os efeitos não seguem uma tendência
   com a idade, e todos os intervalos incluem zero.

Conclusão: com estes dados, **não dá para afirmar que idosos respondem diferente de adultos**. A diferença
que o modelo prevê (cerca de 0,2 mmHg por aumento) é pequena demais para ser detectada; seria preciso
muito mais aumentos de dose. Para separar o efeito da idade do efeito da PAM de partida, o próximo passo é
uma regressão com idade (contínua), PAM antes, dose e tamanho do aumento juntos.

### Pontos do relatório (versão de 23/11) a atualizar com o que foi feito aqui

- **2.3:** os valores de complacência estão trocados ("idosos 1,91 mL/mmHg; jovens 0,96"). No modelo, o
  adulto tem 1,91 e o idoso tinha 0,96 (× 0,5); com 0,79 passa a ter 1,51.
- **1.1:** "noradrenalina (> 1 µg/kg/min) é o vasopressor de primeira linha": provavelmente um erro de
  digitação (a dose alta do ATHOS-3 é > 0,2 µg/kg/min).
- **2.4:** descrever a farmacodinâmica da noradrenalina como premissa (tabela acima).
- **2.6 (vazia) e 3.2.5:** trocar o MIMIC demo (33 internações) pelo MIMIC completo (8.276 / 2.909
  internações), os níveis da seção 5 deste README e a diferença em diferenças.
- **3.2.1, 3.2.3 e Tabela 3:** valores do idoso com C × 0,5 (103/29, PP 74; saudável PP 77) mudam com 0,79.
- **4 (Discussão):** "calibrar a farmacodinâmica da noradrenalina" está parcialmente respondido: o efeito
  por aumento é pequeno e compatível com a premissa, mas o intervalo ainda não permite calibrar Emax e EC50.

**Os dois modos do modelo (nora fixa + Ang II; desmame da nora + Ang II) foram considerados?**
Até a seção 14, não: a validação usou só a peça da noradrenalina (planta + efeito da nora), sem Ang II, e a PAM
medida durante a Ang II foi descartada. A seção 15 testa o modo 1 (nora fixa + Ang II) com os 29 casos
reais. O modo 2 não foi simulado, mas o desmame aparece nos dados (a nora caiu em 8 dos 21 casos).

**Por que primeiro a noradrenalina e depois a Ang II?**
O modo da Ang II é construído por cima da noradrenalina de fundo: se a base estiver errada, a Ang II herda o
erro. Os 29 pacientes com Ang II correspondem à segunda etapa (todos já estavam com nora em cerca de 0,5),
não à primeira.

**A Ang II pode ser validada com tão poucos dados?**
Só como série de casos, com controles pareados, e declarando todas as limitações (ver "Angiotensina II no
MIMIC"). O teste quantitativo mais forte continua sendo a coorte virtual contra o ATHOS-3, lembrando que a
calibração veio do próprio ATHOS-3.

## 8. Próximos passos sugeridos

- [x] Recalibrar `FATOR_C_IDADE` (0,79 nesta cópia; levar ao repositório principal quando o grupo aprovar).
- [x] Diferença em diferenças para a resposta a cada aumento de dose (seção 14).
- [x] Proxy de refratário alternativo (precisou de 2º vasopressor).
- [ ] Diferença em diferenças pareando também pela **tendência** da PAM (não só o nível), e por tamanho do
      aumento de dose (efeito por 0,01 µg/kg/min).
- [ ] Regressão da resposta a cada aumento de dose com idade contínua, PAM antes, dose e tamanho do aumento.
- [ ] Reescrever o teto da nora (critério 4) para que não dependa da PAM de partida, ou justificar essa escolha.
- [x] Ang II no MIMIC: 21 casos com controles pareados (seção 15).
- [ ] Parear os controles da Ang II também pela **tendência** (PAM e nora piorando × melhorando nas horas anteriores).
- [ ] Nível 4: coorte virtual contra o ATHOS-3, comparando o **efeito** (diferença entre braços), não só o braço Ang II.
- [ ] Investigar a forma da onda (Q_in, Windkessel de 4 elementos) para corrigir a PAD.
- [ ] Representar a recuperação espontânea (volume, controle da infecção) se o objetivo for reproduzir a
      PAM da população ao longo de horas.
- [ ] Definição de sepse mais rigorosa (Sepsis-3, com SOFA e lactato) em vez de só o CID.

## 9. Limitações para lembrar

- Dados de **um** hospital americano; a idade do MIMIC é deslocada para anonimizar (mas preserva a idade real).
- Sepse identificada só pelo CID, registrado na alta, o que é impreciso.
- A PA não invasiva é intermitente e menos confiável; a invasiva tem prioridade.
- O DC medido existe quase só em pacientes de cirurgia cardíaca.
- O modelo representa só a noradrenalina e a Ang II; a PAM medida com outros vasopressores correndo é descartada.
- Dados observacionais: a dose responde à PAM (viés de indicação). A diferença em diferenças reduz esse
  problema, mas não o elimina.
