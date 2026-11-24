# Resultados da validação: documento de referência para o relatório

*Versão de 23/11/2026. Todos os números foram tirados dos arquivos de resultado desta pasta (nada de memória).
Siglas em [00_GLOSSARIO.md](00_GLOSSARIO.md); como rodar e onde está cada arquivo em [README.md](README.md).*

Este documento junta **tudo o que foi analisado**: o que o modelo afirma, como cada afirmação foi testada,
os números de cada teste, o que foi validado, o que não foi e por quê. A seção 4 compara diretamente as
**variações de PAM** do modelo e dos pacientes reais. A seção 9 sugere como levar isso para o relatório.

---

## Índice

1. O modelo e o que ele afirma
2. Dados, coortes e definições
3. Resultados, teste por teste
4. Variações da PAM: modelo × pacientes reais (quadro-resumo)
5. Placar: o que foi validado, o que é parcial, o que falhou e o que não é testável
6. Problemas do modelo descobertos na validação
7. Decisões tomadas e por quê
8. Limitações gerais
9. Como levar isso para o relatório
10. Onde estão os arquivos e figuras

---

## 1. O modelo e o que ele afirma

### 1.1 Estrutura

- **Planta:** Windkessel de 3 elementos (0D). PAM = (R_p + Z_c) × DC. A complacência C só muda a forma da
  onda (PAS, PAD, PP), não a PAM.
- **Choque:** R_p baixa (RVS 455 dyn·s·cm⁻⁵) e DC alto (10,19 L/min no adulto e 9,5 no idoso), vindos de
  sepse hiperdinâmica (Melo & Peters 1999). FC de 90.
- **Idade:** o idoso tem R_p × 1,15 e C × **0,79** (era 0,5; ver a seção 7).
- **Fármacos:** cada um é uma curva de Hill sobre R_p, e os efeitos se somam:
  R_p(t) = R_p,choque × (1 + E_nora + E_AngII).
- **Dois modos de simulação:**
  - modo 1 (`titular`): noradrenalina de fundo **fixa** (efeito não modelado) e Ang II titulada como no
    ATHOS-3 (começa em 20, ajustes a cada 5 min, máximo 80 ng/kg/min, meta 75);
  - modo 2 (`troca`): 60 min só de noradrenalina, titulada pela regra do grupo (meta 65), e depois a Ang II
    entra e a noradrenalina é desmamada.

### 1.2 De onde vem cada parâmetro (isso importa para saber o que é "validação")

| Bloco | Parâmetro | Valor | Origem |
|---|---|---|---|
| Planta | R_p, C do adulto | 0,91 e 1,91 | **Calibração** (PA 124/74 do adulto saudável) |
| Planta | Z_c | 6% de R_p | Literatura (Westerhof 2009) |
| Planta | RVS e DC do choque | 455 e 10,19 | Literatura (Melo & Peters 1999) |
| Idade | R_p × 1,15 | — | Literatura (Westerhof 2009) |
| Idade | C × 0,79 | — | **Calibração com o MIMIC** (este trabalho); era 0,5 pela literatura |
| Nora | t½ | 2 a 6,8 min | Literatura (Beloeil 2005) |
| Nora | Emax | 0,5 × (65 / PAM_choque − 1) | **Premissa do grupo**: o teto vem do critério 4 |
| Nora | EC50 | 0,2 µg/kg/min | **Premissa do grupo**: reaproveita o limiar de dose alta do ATHOS-3 |
| Ang II | Emax, EC50 | 0,5 e 54,4 ng/kg/min | **Calibração** com subgrupos do ATHOS-3 (Leisman 2024) |
| Ang II | r do BRA | 11,9 | **Calibração** com o subgrupo BRA do ATHOS-3 (22 pacientes) |
| Ang II | t½ | 1 min | Literatura (bula) |

**Consequência:** um teste só é validação independente se usar dados que **não** entraram na calibração.
Comparar a Ang II com o ATHOS-3 é circular; comparar a PP do idoso com o MIMIC também passou a ser, depois
que o fator 0,79 foi tirado do MIMIC.

### 1.3 O que o modelo afirma (as hipóteses que testamos)

1. A PAM no choque, sem remédio, fica abaixo de 65 (58 no adulto, 62 no idoso).
2. O idoso tem pressão de pulso maior que o adulto (complacência menor).
3. A noradrenalina tem efeito pequeno e saturado no refratário: sozinha não leva a PAM a 65 (critério 4).
4. O refratário responde menos à noradrenalina que o não refratário.
5. A Ang II, somada à noradrenalina, leva a PAM à meta de 75 nos pacientes sem BRA.
6. O BRA crônico impede a resposta à Ang II; o BRA pesa mais que a idade.
7. O F15 (fração do déficit corrigida em 15 min) separa cedo quem responde de quem não responde.

---

## 2. Dados, coortes e definições

### 2.1 Fonte

MIMIC-IV (versão: conferir na página de download do PhysioNet), UTIs do Beth Israel Deaconess (Boston),
dados anonimizados, acesso credenciado. Tabelas: `icustays`, `patients`, `admissions`, `diagnoses_icd`,
`inputevents`, `chartevents`, `d_items` e `prescriptions`. Os arquivos (até 30 GB descompactados) foram
convertidos para Parquet com DuckDB, guardando só as linhas úteis (o chartevents foi de 2,5 GB para 71 MB).

### 2.2 Fluxograma

| Etapa | Internações |
|---|---|
| UTI com noradrenalina | 12.841 |
| − unidade de dose desconhecida ou dose > 3 µg/kg/min | 12.657 (184 saem) |
| − sem pressão arterial registrada | 12.655 |
| − noradrenalina iniciada < 60 min após a entrada na UTI (sem PAM "antes") | **8.276 (7.429 pacientes): coorte "todos"** |
| com sepse por CID | 3.724 |
| sem choque cardiogênico | 3.363 |
| sem choque hipovolêmico/traumático | 3.255 |
| fora das UTIs cardiovascular e coronariana | **2.909 (2.646 pacientes): coorte "vasodilatador"** |
| … com PAM antes da noradrenalina (nível 1) | 2.069 |
| … com PAM antes e depois (nível 2) | 1.801 pacientes, 10.118 medidas |

Coorte "todos": 5.470 com PAM antes; nível 2 com 4.446 pacientes e 27.071 medidas.

### 2.3 Definições e filtros

- **Tempo zero:** início da noradrenalina (início da Ang II na análise da Ang II). Janela de −60 a +240 min.
- **Adulto:** 18 a 64 anos; **idoso:** ≥ 65. O modelo representa 46 e 70 anos.
- **PAM:** a invasiva tem prioridade; a não invasiva entra quando não há invasiva num raio de 30 min.
- **Artefatos:** PAM fora de 30–180 mmHg; com PAS e PAD presentes, exige-se PAD < PAM < PAS e PP ≥ 10.
- **Outros vasopressores:** a PAM medida enquanto vasopressina, adrenalina, fenilefrina, dopamina ou Ang II
  corriam foi descartada (cerca de 24% das medidas na coorte vasodilatador).
- **PAM basal:** média das medidas com t ≤ 0 (até 60 min antes).
- **Refratário:** duas definições. (a) "dose": ≥ 6 h com noradrenalina ≥ 0,2 µg/kg/min (proxy, não é
  diagnóstico); (b) "2º vasopressor": recebeu outro vasopressor ou Ang II na UTI.
- **Sepse:** CID-9/10 (A40, A41, R65.20, R65.21, 038, 995.91/92, 785.52). É o diagnóstico da alta, impreciso.
- **IECA/BRA:** prescrições hospitalares; **não** representam uso crônico em casa.

---

## 3. Resultados, teste por teste

Para cada teste: o que foi feito → números → veredito → ressalvas. Os números são da coorte
**vasodilatador**, salvo quando indicado "todos".

### 3.1 Verificação numérica (nível 0): o código resolve as equações certas?

- **Feito:** cenário idoso sem IECA/BRA simulado pelo Windkessel completo (Euler, 0,1 ms) e pela
  aproximação quase-estática usada nas 3 h.
- **Números:** PAM em 1 h de 74,74 e 74,74; em 3 h de 75,00 e 75,00; dose final de 38,45 e 38,45 ng/kg/min.
- **Veredito: PASSA.** Diferença < 0,01 mmHg.
- **Valores das plantas com C × 0,79** (`verificar.jl`):

| Cenário | Modelo agora | Documento antigo (C × 0,5) |
|---|---|---|
| Adulto saudável | 124/74, PAM 95, PP 50 | 124/74, PAM 95, PP 50 |
| Idoso saudável | 134/77, PAM 102, PP 57 | 145/68, PAM 102, PP 77 |
| Choque adulto | 81/38, PAM 58, PP 44 | igual |
| Choque idoso | 89/39, PAM 62, PP 51 | 103/29, PAM 62, PP 74 |

A PAM não muda com C, como esperado (Eq. 6 do relatório). Mudam só PAS, PAD e PP do idoso.

### 3.2 Planta antes do tratamento (nível 1)

- **Feito:** PAM, PAS, PAD e PP basais (antes da noradrenalina), comparadas às do modelo.
  **Critério:** o modelo dentro do IIQ dos pacientes.
- **Números (mediana e IIQ dos pacientes × modelo):**

| | Adulto real | Modelo adulto | Idoso real | Modelo idoso |
|---|---|---|---|---|
| PAM | 63 (56–74) | 58 ✓ | 64 (55,5–73) | 62 ✓ |
| PAS | 92,5 (83–107) | 81 ✗ | 95 (84–110) | 89 ✓ |
| PAD | 52,5 (45–62,5) | 38 ✗ | 52 (44–61) | 39 ✗ |
| PP | 40 (32–50) | 44 ✓ | 42 (33–55) | 51 ✓ |

  Coorte "todos": PAM 66/65, PAS 95/97, PAD 54/52, PP 41/44 (medianas adulto/idoso). Conclusões iguais.
- **Veredito:**
  - **PAM: PARCIAL.** Dentro do IIQ, mas abaixo da mediana (5 mmHg no adulto, 2 no idoso), e o IIQ é largo
    (cerca de 18 mmHg), então o critério é fraco.
  - **PAD: NÃO PASSA.** O modelo fica 13 a 15 mmHg abaixo, nos dois grupos.
  - **PP: PASSA**, mas só depois da recalibração de C (antes era 74 no idoso). Por isso não é independente.
- **Diferença adulto × idoso nos pacientes:** praticamente nenhuma (PAM 63 × 64, PP 40 × 42, PAD 52,5 × 52).
  O modelo separa mais as idades (PP 44 × 51) do que os pacientes reais.
- **Por que a PAD erra (e não se corrige com C):** nos pacientes, a PAM fica a cerca de 1/3 do caminho entre
  a PAD e a PAS (52 + 42/3 ≈ 66); no modelo, perto da metade. Testando C de 0,25 a 3,0 vezes o do adulto,
  a PP chega a 42 com fator 1,0, mas a pressão fica em 84/42, nunca em 95/52. É a forma da onda: ejeção em
  meia senoide e Windkessel sem reflexão de onda. Corrigir exigiria mudar Q_in ou usar um Windkessel de 4 elementos.

### 3.3 Planta com entradas reais (FC e DC de cada paciente; problema inverso)

- **Feito:** (A) o modelo recebeu a FC (e, quando existia, o DC medido) de cada paciente; (B) para cada
  paciente, calculamos que R_p e C reproduzem a PAM e a PP dele.
- **Números:**
  - Coorte "todos": FC real em 8.272 internações; **DC medido em só 1.222**, e só 126 com DC antes da
    noradrenalina (82% delas na UTI cardiovascular, ou seja, pós-cirurgia cardíaca, e só 6% com sepse).
    Na coorte vasodilatador, só 11 com DC antes da noradrenalina.
  - Usar a FC real **não melhora** a previsão. Usar o DC real com o R_p do modelo faz a PAM cair cerca de
    40 mmHg, porque o R_p do modelo foi feito para DC de 10 L/min.
  - **DC medido:** 5,3 L/min no adulto e 4,2 no idoso (coorte "todos"), contra 10,2 / 9,5 no modelo.
    RVS de cerca de 1.100 / 1.300, contra 455 no modelo.
  - **Razão idoso/adulto calculada a partir dos dados:**

| Fonte do DC | R_p (modelo 1,15) | C (modelo 0,79; literatura 0,25–0,50) |
|---|---|---|
| DC medido, todos (126) | 1,20 | 0,75 |
| DC medido, vasodilatador (11) | 1,35 | 0,81 |
| DC da literatura, vasodilatador (2.028) | 1,08 | 0,90 |

  - A C calculada cai com a idade quando o DC é medido (1,29 → 0,95 → 0,84 → 0,70 ml/mmHg de 18 a 85 anos),
    mas não mostra tendência clara quando se usa o DC da literatura.
- **Veredito:**
  - R_p × 1,15 com a idade: **coerente**.
  - C × 0,5 (literatura): **contrariado**; os dados indicam de 0,75 a 0,9, e daí a escolha de 0,79.
  - Fenótipo hiperdinâmico (DC 10, RVS 455): **não confirmado nem descartado**. Quase não há DC medido em
    sépticos, e os que existem são de pacientes cardíacos, que não representam o choque vasodilatador.

### 3.4 PAM da população depois da noradrenalina

- **Feito:** PAM média alinhada ao início da noradrenalina (bins de 5 min). O modelo recebe a dose média
  real (cerca de 0,13 µg/kg/min) e parte da PAM do próprio modelo.
- **Números (PAM média dos pacientes):**

| | Antes (−60 a 0) | 30–120 min | 180–240 min | Variação |
|---|---|---|---|---|
| Adulto real (vasodilatador) | 67,1 | 71,0 | 72,0 | **+4 a +5** |
| Idoso real (vasodilatador) | 65,4 | 70,0 | 70,9 | **+5 a +5,5** |
| Adulto real ("todos") | 68,9 | 73,8 | 74,1 | +5 |
| Idoso real ("todos") | 67,5 | 71,6 | 71,9 | +4,5 |
| Modelo adulto (dose média real) | 58 | ≈ 59,5 | ≈ 59,5 | **≈ +1,5** |
| Modelo idoso (dose média real) | 62,1 | ≈ 62,8 | ≈ 62,8 | **≈ +0,7** |

  Obs.: aqui a PAM "antes" é a média dos bins de tempo (67/65); na seção 3.2 é a mediana por paciente (63/64).
- **Veredito: NÃO PASSA como descrição da população tratada.** O modelo fica 8 a 10 mmHg abaixo depois da
  noradrenalina.
- **Mas** a seção 3.7 mostra que quase toda a subida real é regressão à média e recuperação espontânea
  (volume, controle da infecção), e não efeito da noradrenalina. O modelo não tem esses mecanismos.

### 3.5 Previsão da PAM de cada paciente (nível 2)

- **Feito:** malha aberta com a dose real de cada paciente; PK de 1 compartimento (t½ 4,4 min); Emax e EC50
  ajustados por busca em grade; validação cruzada por paciente em 5 partes. Dois modelos: **A** parte da PAM
  basal do paciente; **B** parte da PAM do grupo (58/62). Duas referências: "a PAM fica igual" e "média da
  população". **Critério:** o modelo ganha das duas referências (habilidade > 0).
- **Números (coorte vasodilatador; 10.118 medidas, 1.801 pacientes):**

| Preditor | Viés | RMSE | Erro ≤ 10 mmHg | Habilidade | CCC de Lin | Limites de 95% (Bland-Altman) |
|---|---|---|---|---|---|---|
| Modelo A | −3,4 | 19,0 | 49% | −0,44 | 0,21 | −40 a +33 |
| Modelo B | −9,6 | 16,5 | 52% | −0,25 | −0,01 | −36 a +17 |
| Ref.: PAM fica igual | −4,2 | 19,0 | 49% | — | 0,21 | −41 a +32 |
| Ref.: média da população | 0,0 | **13,2** | 62% | — | 0 | −26 a +26 |

  Coorte "todos": RMSE A 18,8, B 18,1, referência 14,2; habilidade −0,32 e −0,28. Adultos e idosos
  separadamente dão o mesmo padrão (habilidade de −0,14 a −0,48).
- **Ajuste da noradrenalina:** Emax ≈ 0,02 com EC50 no limite da grade (0,01). Ou seja, o melhor ajuste é
  "efeito quase zero", e os parâmetros não são identificáveis com estes dados.
- **Dose × PAM:** a PAM mediana fica entre 67 e 70 mmHg em todas as faixas de dose, de 0,03 a 0,5 µg/kg/min.
  A curva é plana.
- **Veredito: NÃO PASSA.** O modelo A empata com "a PAM fica igual" (o efeito da noradrenalina não acrescenta
  nada), e os dois perdem para a média da população.
- **Por que (e por que isso não é o teste certo):** (1) **viés de indicação**: a dose sobe quando a PAM cai,
  o que esconde o efeito; (2) **regressão à média**; (3) o modelo representa um paciente típico, não cada
  paciente. Esse teste segue o documento de metodologia, mas não mede o que o modelo afirma. O teste
  adequado é o da seção 3.7.
- **Bland-Altman do modelo B:** a faixa diagonal não é defeito do gráfico. Um preditor quase constante
  (62 mmHg) gera erros sobre uma reta inclinada.

### 3.6 Critério 4 (nível 3): no refratário, noradrenalina ≥ 0,2 deixa a PAM abaixo de 65?

- **Feito:** fração das medidas de PAM < 65 enquanto a dose era ≥ 0,2. **Critério:** > 50% nos refratários.
- **Números:**

| Coorte | Refratários | Não refratários |
|---|---|---|
| Vasodilatador | **42%** < 65 (1.461 medidas; mediana 66) | 24% (757; mediana 73) |
| Todos | **37%** < 65 (3.290; mediana 69) | 27% (2.124; mediana 72) |

- **Veredito: NÃO PASSA** como está escrito (o modelo assume 100%).
- **Ressalvas:** a equipe titula a dose justamente até 65 e acrescenta outros vasopressores (cuja PAM foi
  descartada), e o proxy de refratário é fraco. O critério 4 ao pé da letra não é observável em dados de rotina.

### 3.7 Efeito de cada aumento de noradrenalina: diferença em diferenças (o teste central)

- **Ideia:** comparar **o mesmo tipo de situação com e sem aumento de dose**. Assim a regressão à média, que
  existe nos dois casos, se cancela.
- **Desenho:**
  - **Evento:** aumento de dose ≥ 20% e ≥ 0,02 µg/kg/min, com a noradrenalina já correndo (mediana do
    aumento: +0,05; metade entre +0,03 e +0,10).
  - **Controle:** instantes de dose estável (nenhuma mudança ≥ 20% de 30 min antes até 45 min depois).
  - **Variação:** PAM média de 15 a 45 min depois menos a dos 30 min antes.
  - **Pareamento:** mesma faixa de PAM prévia (5 mmHg) e mesma faixa de dose (< 0,2 ou ≥ 0,2).
  - **IC de 95%:** bootstrap por paciente (300 réplicas).
  - **Modelo:** a mesma fórmula do modelo aplicada a cada aumento real.
- **A regressão à média aparece claramente:** partindo de 45–55 mmHg, a PAM sobe de 11 a 20 mmHg **com ou
  sem** aumento de dose; acima de 75 ela cai. As curvas "aumento" e "estável" quase se sobrepõem.
- **Números (vasodilatador: 760 aumentos, 4.314 períodos estáveis):**

| Recorte | Subida bruta após o aumento | Subida nos controles | **Efeito do aumento (IC 95%)** | Modelo |
|---|---|---|---|---|
| Todos | +5,3 | +4,7 | **+0,6 (−0,4 a +1,7)** | +0,25 |
| Dose < 0,2 | +5,4 | +4,3 | +1,0 (0,0 a +2,2) | +0,25 |
| Dose já ≥ 0,2 | +4,8 | +8,0 | −3,2 (−7,9 a +0,6) | +0,22 |
| Adulto | +5,9 | +4,9 | +1,1 (−0,5 a +2,6) | +0,36 |
| Idoso | +4,9 | +4,3 | +0,6 (−0,9 a +2,1) | +0,15 |
| Refratário (dose) | +4,3 | +4,0 | **+0,2 (−1,4 a +1,8)** | +0,25 |
| Não refratário (dose) | +6,3 | +4,6 | **+1,7 (+0,4 a +3,1)** | +0,24 |
| Refratário (2º vasopressor) | +4,8 | +4,3 | +0,5 (−1,1 a +1,8) | +0,25 |
| Não refratário (2º vasopressor) | +6,2 | +5,2 | +0,9 (−0,4 a +2,5) | +0,24 |
| 2º vasopressor e dose ≥ 0,2 | +4,3 | +7,3 | −3,0 (−10,2 a +0,9) | +0,21 |

- **Coorte "todos" (2.050 aumentos):** efeito **+2,1 (+1,4 a +2,7)**; refratário +1,3 (+0,3 a +2,7);
  não refratário +2,8 (+1,9 a +3,8). O modelo (+0,26) fica **abaixo** do intervalo.
- **Veredito:**
  - Choque vasodilatador: **PASSA.** O efeito do modelo cai dentro do IC dos dados; o efeito é pequeno e
    praticamente nulo no refratário e com dose alta. **Isso apoia a premissa central do trabalho.**
  - UTI em geral ("todos"): **NÃO PASSA.** A noradrenalina tem efeito claro (cerca de +2 mmHg por aumento), e o
    modelo subestima. Isso é coerente: o modelo representa só o choque refratário.
- **Atenção na escrita:** o +0,25 do modelo **não é uma previsão livre**, porque vem das premissas do grupo
  (teto do critério 4 × 0,5 e EC50 de 0,2). O correto é dizer: "a premissa é compatível com os dados".
- **Ressalvas:** o pareamento é pelo nível da PAM, não pela tendência. Se a equipe aumenta a dose quando a
  PAM *está caindo*, o efeito real é maior que o medido. Os aumentos são pequenos e a PAM não invasiva é
  esparsa (a cada 15 a 60 min).

### 3.8 O refratário responde menos? (premissa central)

- **Dados (seção 3.7):** refratário ≈ 0 (+0,2; IC −1,4 a +1,8), não refratário +1,7 (IC +0,4 a +3,1);
  dose já ≥ 0,2: −3,2 (IC −7,9 a +0,6).
- **Comparação ingênua (antes de descontar a regressão à média):** a PAM subia cerca de +5 mmHg em todos os
  grupos, o que parecia contradizer a teoria. Era regressão à média.
- **Modelo:** mostra a falta de resposta porque ela foi **imposta** (o teto), e não existe no modelo um paciente
  não refratário para comparar.
- **Veredito: PASSA (com ressalvas).** Os dados apoiam a premissa no choque vasodilatador; o modelo a
  representa por construção.

### 3.9 Adulto × idoso

- **Antes do tratamento:** não há diferença relevante (seção 3.2). Refratários: 37% dos adultos e 32% dos idosos.
- **Resposta a cada aumento de noradrenalina:** adulto +1,1 (IC −0,5 a +2,6), idoso +0,6 (IC −0,9 a +2,1).
  **Diferença adulto − idoso: +0,5 mmHg (IC −1,6 a +2,5)**, calculada com o próprio IC por bootstrap de
  pacientes (comparar os dois intervalos separados não basta). Ou seja, não detectável.
- **Por faixa de idade:** 18–49 anos +2,9; 50–64 +0,3; 65–74 +0,2; 75–84 +2,1; ≥ 85 −2,0. Não há tendência, e
  todos os intervalos incluem zero.
- **Modelo:** prevê cerca de 2,5 vezes mais efeito no adulto (+0,36 × +0,15). Essa diferença **não vem de
  farmacologia do envelhecimento**, e sim do teto: o idoso parte de uma PAM maior (62 contra 58), então
  sobra menos espaço até 65.
- **Veredito: INCONCLUSIVO.** Com cerca de 760 aumentos de dose, não dá para detectar uma diferença de
  0,2 mmHg. Para separar o efeito da idade do efeito da PAM de partida, seria preciso uma regressão com
  idade contínua.

### 3.10 Angiotensina II nos pacientes reais (MIMIC): casos × controles pareados

- **Desenho:**
  - **Casos:** 29 internações com Ang II. Saíram 2 sem PAM basal, 6 sem PAM na hora 3 e 1 sem
    noradrenalina válida, restando **22**; destas, **21** tiveram controle pareado.
  - **Controles:** internações que nunca receberam Ang II, num instante com noradrenalina ≥ 0,4 µg/kg/min;
    até 5 por caso, com PAM basal (±5 mmHg), noradrenalina (±0,15) e sepse parecidas. Mediana de 5
    controles por caso, entre 2.547 possíveis.
  - **Desfecho do ATHOS-3** na hora 3 (média de 150–210 min): PAM ≥ 75 ou subida ≥ 10, sem aumentar
    outros vasopressores.
  - **Modelo:** modo 1 (noradrenalina fixa) com a PAM basal e as **doses reais** de Ang II de cada caso;
    Emax 0,5 e r = 1.
  - **Doses:** em ng/kg/min e µg/kg/min (× 1000); 1 registro implausível (405 ng/kg/min) excluído.
- **Perfil dos casos:** todos já com noradrenalina alta (mediana de cerca de 0,5); a maioria começou com
  20 ng/kg/min (a dose do ATHOS-3); PAM esparsa (mediana de cerca de 5 medidas de −1 a +3 h).
- **Números:**

| Fonte | Responderam com Ang II | Controle / placebo | **Efeito (pontos percentuais)** |
|---|---|---|---|
| ATHOS-3 (randomizado, 163 × 158) | 69,9% | 23,4% | **+46,5 (36,9 a 56,2)** |
| MIMIC pareado (21) | 33% | 25% | **+8,6 (−13 a +31)** |
| MIMIC, PAM basal 55–70 como no ATHOS-3 (13) | 23% | 14% | +9,2 (−17 a +39) |
| Modelo, Emax 0,5 (doses reais) | 67% | 0% (sem placebo) | +67 (62 a 67 com Emax 0,3–1,0) |
| Modelo, se todos tivessem BRA (r = 11,9) | 19% | 0% | +19 |

  - **Variação da PAM em 3 h:** casos +3,4, controles +4,8, ou seja, efeito de **−1,4 mmHg (IC −6,9 a +4,4)**.
    O modelo prevê **+11,1 mmHg** (+11,6 no recorte 55–70, cujo efeito real foi −1,7, IC −9,9 a +7,1).
  - **Noradrenalina em 3 h:** casos −0,06 e controles −0,18 µg/kg/min (diferença +0,12; IC +0,03 a +0,19). Os
    controles reduziram **mais** a noradrenalina, o que sugere que os casos estavam piorando. A noradrenalina
    caiu em 8 dos 21 casos.
  - Resposta só pela PAM (ignorando a regra dos vasopressores): 43% dos casos.
- **Veredito: INCONCLUSIVO, com sinal contra o modelo.** O efeito real foi bem menor que no ensaio e no
  modelo, e os intervalos do MIMIC e do ATHOS-3 nem se cruzam. Mas não dá para concluir, pelos motivos abaixo.
- **Ressalvas (todas precisam constar):** n mínimo; PAM esparsa (1 ou 2 medidas por janela); não
  randomizado (a Ang II é resgate e os casos estavam piorando, o que o pareamento por nível não captura);
  regressão à média (descontada pelo controle); **sem dado de BRA crônico** (o fator r não é testável);
  noradrenalina fixa no modelo; o modelo não tem placebo (comparar o **efeito**, não a % do braço); critério
  de entrada diferente (o ATHOS-3 exigia PAM 55–70); meta clínica diferente (65 × 75); um único centro e
  uso recente da Ang II (aprovada no fim de 2017).

### 3.11 Angiotensina II no modelo × ATHOS-3 (sem dado novo)

- **Cenários do modelo (Emax 0,5; `verificar.jl`):**

| Cenário | PAM em 3 h | Tempo até 75 | Dose final | F15 | PAS/PAD em 3 h |
|---|---|---|---|---|---|
| Adulto sem IECA/BRA | 74,9 | 106 min | 76,5 | 0,68 | 100/53 |
| Idoso sem IECA/BRA | 75,0 | 45 min | 38,4 | 0,82 | 103/50 (era 116/40 com C × 0,5) |
| Idoso com BRA | 65,6 | não atinge | 80 (saturada) | 0,15 | 93/42 (era 106/32) |

- O modelo reproduz o braço Ang II do ATHOS-3 (67% de respondedores com as doses dos casos do MIMIC,
  contra 69,9%). **Isso não é validação**, porque a Ang II foi calibrada com o próprio ATHOS-3.
- **Não feito:** coorte virtual comparando o **efeito** (diferença entre braços) e os desfechos
  secundários do ensaio (conferir os números no artigo completo).
- **Veredito: NÃO VALIDADO** (só a calibração reproduz o ensaio).

---

## 4. Variações da PAM: modelo × pacientes reais (quadro-resumo)

Este é o quadro para comparar "quanto a PAM muda" em cada situação.

| Situação | Pacientes reais | Modelo | Comentário |
|---|---|---|---|
| PAM no choque, sem remédio | 63 / 64 (mediana; IIQ 56–74) | 58 / 62 | Dentro do IIQ, abaixo da mediana |
| Subida após o início da noradrenalina (população, 30–240 min) | **+4 a +5,5** | **+0,7 a +1,5** | A subida real é quase toda regressão à média e recuperação espontânea |
| Efeito de cada aumento de nora, descontada a regressão à média (vasodilatador) | **+0,6** (IC −0,4 a +1,7) | +0,25 | **Compatível** |
| … idem, coorte "todos" | +2,1 (IC +1,4 a +2,7) | +0,26 | Modelo abaixo: ele só representa o refratário |
| … no refratário | +0,2 (IC −1,4 a +1,8) | +0,25 | Compatível: ≈ 0 |
| … no não refratário | +1,7 (IC +0,4 a +3,1) | +0,24 | Modelo abaixo |
| … com dose já ≥ 0,2 | −3,2 (IC −7,9 a +0,6) | +0,22 | Compatível: ≈ 0 |
| … adulto × idoso | +1,1 × +0,6 (diferença +0,5; IC −1,6 a +2,5) | +0,36 × +0,15 | Sem diferença detectável nos dados |
| Efeito máximo possível da nora (dose infinita) | não mensurável | +3,5 (adulto) / +1,4 (idoso) | Imposto pelo teto do critério 4 |
| Efeito máximo da nora se o DC do idoso for baixado para 7,3 (PAM 47,7) | — | **+8,7** | Defeito: o teto cresce quando a PAM cai (seção 6) |
| PAM com nora ≥ 0,2 no refratário | 42% < 65 (mediana 66) | 100% < 65 | O critério 4 ao pé da letra não se sustenta |
| Ang II, variação da PAM em 3 h (MIMIC, descontado o controle) | **−1,4** (IC −6,9 a +4,4) | **+11,1** | Inconclusivo (n = 21) |
| Ang II, respondedores a mais | +8,6 pp (MIMIC) / +46,5 pp (ATHOS-3) | +67 pp | O modelo não tem placebo; o ATHOS-3 é circular |
| Ang II com BRA | não testável (sem dado de BRA) | +3,5 (de 62 para 65,6) | Calibração com 22 pacientes do ATHOS-3 |
| Ang II sem BRA (simulação de 3 h) | — | +13 a +17 (até a meta de 75) | Calibrado no ATHOS-3 |

**Leitura geral:** no choque vasodilatador real, **quase nada do que se faz muda a PAM a curto prazo de forma
mensurável**. A PAM se recupera sozinha (regressão à média e recuperação), e cada aumento de noradrenalina
acrescenta menos de 1 mmHg. O modelo acerta essa parte (efeito pequeno da nora no refratário), mas: (1) não
tem a recuperação espontânea, por isso fica abaixo da PAM da população; (2) dá à Ang II um efeito grande,
calibrado no ensaio, que os 21 casos reais não mostraram (inconclusivo).

---

## 5. Placar

### Validado (os dados apoiam)
- **Verificação numérica** (código correto).
- **PAM sem tratamento** numa faixa plausível (critério fraco).
- **R_p maior no idoso** (× 1,15): coerente com o problema inverso.
- **Efeito pequeno da noradrenalina** por aumento de dose no choque vasodilatador (+0,6 real × +0,25 modelo).
- **Refratário não responde** à noradrenalina (efeito ≈ 0) e não refratário responde (+1,7). A premissa
  central do trabalho é **compatível** com os dados (mas foi imposta, não prevista).

### Parcial
- **PAM basal:** dentro do IIQ, abaixo da mediana.
- **Pressão de pulso do idoso:** passa só depois de recalibrar C com os próprios dados (não independente).

### Não passou
- **PAD** (forma da onda): 13 a 15 mmHg abaixo.
- **PAM da população depois da noradrenalina:** cerca de 10 mmHg abaixo (o modelo não tem recuperação espontânea).
- **Previsão por paciente** (CCC 0,2; perde para a média da população).
- **Critério 4 literal** (42% e não > 50%).
- **Efeito da noradrenalina na UTI em geral** (o modelo subestima; ele só representa o refratário).
- **Fator de complacência da literatura (0,5)** para o idoso em choque.

### Inconclusivo
- **Diferença adulto × idoso** na resposta à noradrenalina.
- **Ang II nos pacientes reais** (21 casos; sinal contra o modelo).
- **Fenótipo hiperdinâmico** (DC 10, RVS 455): quase não há DC medido em sépticos.

### Não testável com estes dados
- **Fator r do BRA** (sem dado de uso crônico; a calibração já usa o ATHOS-3/Leisman).
- **F15** como marcador precoce (a PAM é esparsa demais nos primeiros 15 min).
- **Modo 2 (desmame)** como trajetória completa (só se observa que a noradrenalina caiu em 8 de 21 casos).

### Não feito
- **Coorte virtual × ATHOS-3** (comparando o efeito, não só o braço Ang II).

---

## 6. Problemas do modelo descobertos na validação

1. **O teto da noradrenalina depende da PAM basal.** Emax = 0,5 × (65 / PAM − 1). Quanto mais grave o choque
   (PAM menor), **maior** o efeito permitido: +0,5 mmHg com PAM 64, +3,5 com 58, +8,7 com 47,7. É o contrário
   da fisiologia do refratário, e é também a origem do "adulto responde 2,5 vezes mais". Aparece no app
   quando se baixa o DC no slider. Opções: teto fixo, teto calculado pela planta padrão, ou documentar.
2. **Forma da onda:** a PAD fica sempre baixa e a PAM fica perto do meio entre PAD e PAS (nos pacientes, a
   1/3). Não se corrige com C.
3. **Sem recuperação espontânea / sem placebo:** sem remédio, a PAM do modelo não muda. Nos pacientes ela
   sobe de 4 a 5 mmHg em horas (e 23% do placebo do ATHOS-3 "responderam").
4. **Fenótipo do choque:** o DC de 10 L/min é de sepse hiperdinâmica; não foi possível confirmá-lo.
5. **Noradrenalina fixa no modo 1:** na vida real ela muda; no modo 1, o efeito dela nem é modelado.
6. **Premissas da noradrenalina** (Emax pelo teto, EC50 = 0,2) não estão descritas no relatório como
   premissas (seção 2.4 só descreve a Ang II).

---

## 7. Decisões tomadas e por quê

| Decisão | Justificativa |
|---|---|
| C do idoso × 0,79 (era 0,5) | Problema inverso: dados indicam de 0,75 a 0,9; o 0,5 vem de idosos saudáveis em pressão normal. **Tornou a PP uma calibração, não validação.** |
| Coorte "vasodilatador" como principal | O modelo representa choque vasodilatador; a coorte "todos" mistura choque cardiogênico e pós-cirurgia cardíaca |
| Início "incidente" da noradrenalina (≥ 60 min após a entrada) | Sem isso não existe PAM "antes" |
| PAM entre 30 e 180 mmHg | Valores fora disso são artefatos (lavagem da linha arterial, digitação) |
| Descartar a PAM com outros vasopressores | O modelo não representa esses fármacos |
| Validação cruzada em 5 partes (e não deixando um paciente de fora) | Com milhares de pacientes, dá o mesmo resultado e é viável |
| Diferença em diferenças como teste central | É o único desenho que desconta a regressão à média e reduz o viés de indicação |
| Comparar o **efeito** da Ang II (diferença entre braços) | O modelo não tem placebo |
| Recorte PAM 55–70 na Ang II | É o critério de entrada do ATHOS-3 |
| Só resumos agregados (≥ 11 por valor) no app; dados por paciente fora do git | Termo de uso do PhysioNet |

---

## 8. Limitações gerais

- Dados observacionais: a dose responde à PAM (viés de indicação). A diferença em diferenças reduz o
  problema, mas não o elimina (não pareia a tendência).
- Um único centro (Boston); idade do MIMIC deslocada para anonimizar (mas a idade real é preservada).
- Sepse identificada pelo CID da alta; refratário por proxy (dose ou segundo vasopressor).
- PAM não invasiva esparsa; a invasiva tem prioridade.
- DC medido quase só em pacientes de cirurgia cardíaca.
- IECA/BRA só de prescrições hospitalares; o uso crônico não é conhecido.
- Ang II: 21 casos analisáveis.
- Calibrações com os próprios dados de comparação (C × 0,79; Ang II com o ATHOS-3) tornam esses testes não
  independentes.
- O modelo é 0D, determinístico e de "paciente típico": não foi feito para prever cada paciente.

---

## 9. Como levar isso para o relatório

### Seção 2.6 (Metodologia da validação)
Fonte e ética (2.1 deste documento); fluxograma (2.2); definições e filtros (2.3); tabela dos níveis com
critério de aceite; desenho de cada teste (3.5, 3.7 e 3.10); deixar explícito o que é **calibração** e o que
é **validação** (1.2); software e reprodutibilidade (README).

### Seção 3.2.5 (Resultados da validação)
- Tabela do placar (seção 5) ou o quadro de variações da PAM (seção 4).
- Figuras: `cel13_fig5.png` (concordância e Bland-Altman), `cel14_fig6.png` (diferença em diferenças),
  `resposta_athos.png` e `casos_individuais.png` (Ang II), e o print da aba 6 do app.
- Frase central sugerida: *"No choque vasodilatador, descontada a regressão à média, cada aumento de
  noradrenalina elevou a PAM em +0,6 mmHg (IC 95% −0,4 a +1,7), e de forma indistinguível de zero nos
  refratários, valores compatíveis com a premissa do modelo (+0,25 mmHg). O modelo, porém, não previu a PAM
  de cada paciente (CCC 0,21), subestimou a PAM da população tratada em cerca de 10 mmHg e não reproduziu a
  pressão diastólica."*

### Seção 4 (Discussão)
- Por que a previsão por paciente não é o teste adequado para um modelo 0D de paciente típico.
- A regressão à média como achado metodológico (a comparação ingênua dava +5 mmHg).
- O teto da noradrenalina dependente da PAM (seção 6) e a forma da onda.
- Ang II: o modelo reproduz o ensaio que o calibrou; nos 21 casos reais o efeito foi menor (inconclusivo).
- Adulto × idoso: a diferença prevista é um artefato do teto; os dados não detectam diferença.

### Seção 5 (Conclusão)
O modelo é defensável como **ferramenta didática e mecanística** do choque refratário: a premissa central
(resposta pequena e saturada à noradrenalina) tem apoio nos dados. Não é um preditor clínico de cada paciente.

### Correções pendentes no relatório (versão de 23/11)
- 2.3: valores de complacência trocados (adulto 1,91; idoso 0,96 → agora 1,51 com 0,79).
- 1.1: "noradrenalina (> 1 µg/kg/min)" provavelmente é > 0,2.
- 2.4: descrever a farmacodinâmica da noradrenalina como premissa.
- 3.2.1, 3.2.3 e Tabela 3: valores do idoso com C × 0,5 (103/29, PP 74; saudável 145/68, PP 77) mudam com
  0,79 (89/39, PP 51; saudável 134/77, PP 57).
- 3.2.5: trocar o MIMIC demo (33 internações) pelos resultados deste documento.
- 4: "calibrar a farmacodinâmica da noradrenalina" está parcialmente respondido.

---

## 10. Onde estão os arquivos e figuras

| O quê | Onde |
|---|---|
| Notebook (extração e análises, seções 1 a 15) | `PBLMODELAGEMCSV.ipynb` |
| Validação níveis 1–3 | `…/validar.jl` → `mimic completo/validacao_vasodilatador/metricas.csv` |
| Planta com entradas reais | `…/planta_individual.jl` → `planta_individual.csv` |
| Diferença em diferenças | seção 14 → `resposta_dose.csv` |
| Ang II × controles | seção 15 → `mimic completo/angiotensina/` (`casos.csv` tem dados por paciente: **não compartilhar**) |
| Figuras da coorte vasodilatador | `mimic completo/validacao_vasodilatador/figuras/` |
| Figuras da coorte "todos" | `mimic completo/validacao/figuras/` |
| Figuras da Ang II | `mimic completo/angiotensina/figuras/` |
| Resumos para o app | `…/dados_mimic/` (gerados por `resumo_mimic.jl`) |
| Aba de validação no app | `…/aba_mimic.jl` (aba 6 · Validação do modelo) |
