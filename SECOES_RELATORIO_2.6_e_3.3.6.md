# Texto para o relatório: seções 2.6 e 3.3.6

*Rascunho pronto para colar no Word. Onde aparece **[ref]**, inserir a referência no formato do relatório.
Números de tabelas e figuras são sugestões; ajustar à numeração do documento. A seção 2.6 não traz resultados
(eles vão para a 3.2.5); os números de pacientes de cada etapa do fluxograma também ficam nos resultados.*

---

## 2.6 Metodologia da validação

### 2.6.1 Objetivo e princípio geral

A validação teve como objetivo verificar se o comportamento do modelo é compatível com o observado em
pacientes reais com choque vasodilatador. Como o modelo é 0D, determinístico e representa um **paciente típico**
(adulto de 46 anos e idoso de 70 anos), e não um paciente específico, a validação não se limitou à previsão
da PAM de cada indivíduo. Ela foi organizada em níveis crescentes de exigência, e cada nível testa uma
afirmação diferente do modelo: a correção numérica, a planta hemodinâmica antes do tratamento, a resposta à
noradrenalina, o comportamento do choque refratário e a resposta à angiotensina II.

Antes de cada teste, os parâmetros foram classificados quanto à origem: **literatura**, **calibração**
(ajustado para reproduzir um dado) ou **premissa do grupo** (Tabela X). Esse cuidado é necessário porque um
teste só constitui validação independente quando usa dados que **não** participaram da calibração. Assim:

- a comparação da Ang II com o ATHOS-3 [ref] não foi considerada validação, pois o Emax, o EC50 e o fator r
  do BRA foram calibrados com subgrupos desse ensaio [ref Leisman 2024];
- o fator de redução da complacência do idoso foi recalibrado com os dados do MIMIC-IV (problema inverso,
  seção 2.6.5), de modo que a pressão de pulso do idoso passou a ser uma calibração, e não uma validação;
- o efeito da noradrenalina previsto pelo modelo decorre de premissas do grupo (Emax derivado do critério 4
  e EC50 de 0,2 µg/kg/min), e por isso a comparação com os dados avalia se essas **premissas são compatíveis**
  com a realidade, e não se o modelo as previu.

**Tabela X – Origem dos parâmetros do modelo.**

| Bloco | Parâmetro | Origem |
|---|---|---|
| Planta | R_p e C do adulto saudável | Calibração (PA 124/74 mmHg) |
| Planta | Z_c = 6% de R_p | Literatura (Westerhof et al., 2009) |
| Planta | RVS e DC do choque | Literatura (Melo & Peters, 1999) |
| Idade | R_p × 1,15 | Literatura (Westerhof et al., 2009) |
| Idade | C × 0,79 | Calibração com o MIMIC-IV (este trabalho) |
| Noradrenalina | t½ (2 a 6,8 min) | Literatura (Beloeil et al., 2005) |
| Noradrenalina | Emax = 0,5 × (65 / PAM_choque − 1) | Premissa do grupo (critério 4) |
| Noradrenalina | EC50 = 0,2 µg/kg/min | Premissa do grupo (limiar de dose alta do ATHOS-3) |
| Angiotensina II | Emax, EC50 e r do BRA | Calibração com o ATHOS-3 (Leisman et al., 2024) |
| Angiotensina II | t½ = 1 min | Literatura (bula) |

### 2.6.2 Fonte de dados e aspectos éticos

Foram utilizados os dados do MIMIC-IV [ref Johnson et al., 2023], base pública e anonimizada de internações
em unidades de terapia intensiva do Beth Israel Deaconess Medical Center (Boston, EUA), disponibilizada pelo
PhysioNet [ref Goldberger et al., 2000] mediante credenciamento e assinatura de termo de uso de dados.
Foram usadas as tabelas de internações em UTI (`icustays`), pacientes (`patients`), admissões (`admissions`),
diagnósticos (`diagnoses_icd`), infusões (`inputevents`), sinais registrados à beira-leito (`chartevents`),
dicionário de itens (`d_items`) e prescrições (`prescriptions`).

Por se tratar de base anonimizada de acesso controlado, não houve contato com pacientes. Em respeito ao termo de
uso, nenhum dado individual foi incluído no aplicativo ou no repositório: o aplicativo recebe apenas resumos
agregados, e todo valor exibido corresponde a no mínimo 11 internações.

Dado o volume dos arquivos (dezenas de gigabytes descompactados), as tabelas foram convertidas para o formato
Parquet com o DuckDB, e só as linhas úteis foram mantidas: os itens de pressão arterial, frequência cardíaca,
débito cardíaco e pressão venosa central do `chartevents`, e as prescrições de IECA e BRA.

### 2.6.3 Seleção da coorte

Foram incluídas as internações em UTI de pacientes com 18 anos ou mais que receberam noradrenalina. Foram
excluídas as internações:

1. com unidade de dose desconhecida ou dose acima de 3 µg/kg/min (erro de registro);
2. sem nenhuma pressão arterial registrada;
3. em que a noradrenalina começou menos de 60 min após a entrada na UTI. Sem esse intervalo não existe uma
   PAM "antes do tratamento" para comparar com a planta de choque do modelo.

O resultado constitui a coorte **"todos"**. Como o modelo representa o choque **vasodilatador**, a análise
principal usou uma subcoorte com:

- diagnóstico de sepse pela CID-9 ou CID-10 (A40, A41, R65.20, R65.21, 038, 995.91, 995.92, 785.52);
- exclusão de choque cardiogênico e de choque hipovolêmico ou traumático;
- exclusão das UTIs cardiovascular e coronariana, onde predominam pacientes no pós-operatório de cirurgia
  cardíaca.

Essa é a coorte **"vasodilatador"**. A coorte "todos" foi mantida como análise de sensibilidade. O
fluxograma com o número de internações em cada etapa é apresentado na seção 3.2.5.

### 2.6.4 Definições operacionais

- **Tempo zero:** início da noradrenalina (início da Ang II na análise da seção 2.6.8), com janela de
  observação de −60 a +240 min.
- **Grupos etários:** adulto de 18 a 64 anos e idoso com 65 anos ou mais, correspondendo aos pacientes de
  46 e 70 anos do modelo.
- **PAM:** a medida invasiva teve prioridade; a não invasiva foi usada quando não havia medida invasiva em
  um raio de 30 min.
- **Remoção de artefatos:** foram descartadas as PAM fora de 30 a 180 mmHg. Quando havia PAS e PAD, exigiu-se
  PAD < PAM < PAS e pressão de pulso ≥ 10 mmHg.
- **Outros vasopressores:** as medidas de PAM obtidas enquanto corria vasopressina, adrenalina, fenilefrina,
  dopamina ou Ang II foram descartadas, pois o modelo não representa esses fármacos (exceto a Ang II, tratada
  em análise própria).
- **PAM basal:** média das medidas nos 60 min anteriores ao início da noradrenalina.
- **Choque refratário:** por não haver um diagnóstico registrado, foram usadas duas definições aproximadas
  (*proxy*): (a) por dose, com pelo menos 6 h de noradrenalina ≥ 0,2 µg/kg/min; (b) por segundo
  vasopressor, quando o paciente recebeu outro vasopressor ou Ang II na UTI.
- **Uso de IECA ou BRA:** prescrição hospitalar desses fármacos. A base não informa o uso crônico domiciliar.

### 2.6.5 Níveis de validação e critérios de aceitação

A Tabela Y resume os testes, o que cada um avalia e o critério de aceitação definido **antes** da análise.

**Tabela Y – Níveis de validação.**

| Nível | Teste | O que avalia | Critério de aceitação |
|---|---|---|---|
| 0 | Verificação numérica | Se o código resolve as equações corretamente | Diferença < 0,01 mmHg entre o Windkessel integrado por Euler (passo 0,1 ms) e a aproximação quase-estática usada nas simulações de 3 h |
| 1 | Planta antes do tratamento | Se a planta de choque reproduz a pressão dos pacientes antes da noradrenalina | PAM, PAS, PAD e PP do modelo dentro do intervalo interquartil (IIQ) dos pacientes, por grupo etário |
| 1b | Planta com entradas reais (problema inverso) | Se os fatores de idade de R_p e C são coerentes com os pacientes | Razão idoso/adulto de R_p e C estimados por paciente comparada aos fatores do modelo |
| 2 | PAM da população após a noradrenalina | Se o modelo reproduz a curva média de PAM alinhada ao início da noradrenalina | Comparação gráfica e numérica com a média ± erro-padrão |
| 2 | Previsão da PAM por paciente | Se o modelo prevê a PAM de cada paciente a partir da dose real | Habilidade > 0, isto é, erro menor que o das referências "PAM constante" e "média da população" |
| 2b | Efeito de cada aumento de noradrenalina (diferença em diferenças) | Se o efeito pequeno da noradrenalina, premissa do modelo, aparece nos dados | Efeito do modelo dentro do IC 95% do efeito observado |
| 3 | Critério 4 | Se, no refratário, a noradrenalina ≥ 0,2 µg/kg/min deixa a PAM abaixo de 65 mmHg | Mais de 50% das medidas abaixo de 65 mmHg nos refratários |
| 3b | Refratário × não refratário | Se o refratário responde menos à noradrenalina | Efeito no refratário compatível com zero e efeito positivo no não refratário |
| 4 | Angiotensina II nos pacientes reais | Se o efeito da Ang II previsto pelo modelo aparece nos casos tratados | Efeito do modelo dentro do IC 95% do efeito observado nos casos em relação aos controles |

**Nível 1b: problema inverso.** Para cada paciente, foram calculados o R_p e a C que reproduzem a PAM e a
pressão de pulso medidas. O R_p foi obtido diretamente de R_p + Z_c = PAM / DC (com Z_c = 6% de R_p), e a C por bisseção logarítmica sobre
a pressão de pulso simulada. Quando havia débito cardíaco medido (termodiluição, contínuo ou NICOM), ele foi
usado; caso contrário, usou-se o DC da literatura adotado no modelo. Esse resultado embasou a recalibração do
fator de complacência do idoso (de 0,5 para 0,79).

**Nível 2: previsão por paciente.** O modelo foi executado em malha aberta com a sequência real de doses de
cada paciente. A farmacocinética usou um compartimento, com meia-vida de 4,4 min e sensibilidade com 2 e
6,8 min. Foram avaliadas duas variantes:

- **A:** parte da PAM basal do próprio paciente;
- **B:** parte da PAM do modelo para o grupo etário (58 ou 62 mmHg).

O Emax e o EC50 da noradrenalina foram reajustados por busca em grade (Emax de 0 a 1,5; EC50 de 0,01 a
2 µg/kg/min em escala logarítmica) com validação cruzada em 5 partes, separadas **por paciente** (semente
fixa), para que nenhum paciente contribuísse ao mesmo tempo para o ajuste e para o teste. As métricas foram:

- viés, RMSE e MAE;
- fração de erros ≤ 10 mmHg;
- coeficiente de concordância de Lin (CCC) [ref Lin, 1989];
- limites de concordância de Bland-Altman [ref Bland & Altman, 1986];
- habilidade (*skill score*), definida como 1 − RMSE_modelo / RMSE da melhor referência.

**Nível 2b: diferença em diferenças.** Em dados observacionais, a dose de noradrenalina é aumentada justamente
quando a PAM cai (viés de indicação), e PAM baixas tendem a subir sozinhas (regressão à média), o que distorce
a comparação direta entre dose e PAM. Para descontar esses efeitos:

- **Eventos:** aumentos de dose ≥ 20% e ≥ 0,02 µg/kg/min com a noradrenalina já em curso.
- **Controles:** instantes de dose estável, sem mudança ≥ 20% entre 30 min antes e 45 min depois.
- **Variação da PAM:** média de 15 a 45 min após o instante menos a média dos 30 min anteriores.
- **Pareamento:** os controles foram pareados por faixa de PAM prévia (5 mmHg) e por faixa de dose
  (< 0,2 ou ≥ 0,2 µg/kg/min).
- **Efeito do aumento:** variação média nos eventos menos a variação média nos controles pareados.
- **IC 95%:** *bootstrap* por paciente (300 réplicas).

O valor do modelo foi obtido aplicando a mesma mudança de dose à planta de choque correspondente (adulto ou
idoso). A análise foi repetida por faixa de dose, por grupo etário, por faixa de idade e por condição de
refratário (nas duas definições). A diferença entre adultos e idosos teve um IC próprio, calculado no mesmo
*bootstrap*.

**Nível 3: critério 4.** Calculou-se a fração das medidas de PAM abaixo de 65 mmHg obtidas enquanto a dose de
noradrenalina era ≥ 0,2 µg/kg/min, separadamente para refratários e não refratários.

### 2.6.6 Angiotensina II: estudo caso-controle pareado

Como a Ang II foi pouco usada no MIMIC-IV, sua avaliação foi feita por um desenho caso-controle pareado, de
caráter **exploratório**.

- **Casos:** internações que receberam Ang II com PAM registrada antes do início e em torno da hora 3.
- **Controles:** até 5 por caso, escolhidos entre internações que nunca receberam Ang II, num instante com
  noradrenalina ≥ 0,4 µg/kg/min, e pareados por PAM basal (±5 mmHg), dose de noradrenalina
  (±0,15 µg/kg/min) e presença de sepse.
- **Doses:** registradas em ng/kg/min ou µg/kg/min e convertidas para ng/kg/min. Valores acima de
  100 ng/kg/min foram considerados implausíveis e excluídos.
- **Desfecho:** a mesma definição de resposta do ATHOS-3 [ref Khanna et al., 2017], avaliada na hora 3 (média
  de 150 a 210 min): PAM ≥ 75 mmHg ou aumento ≥ 10 mmHg, sem aumento de outros vasopressores. Desfechos
  secundários: a variação da PAM e da dose de noradrenalina em 3 h.
- **Modelo:** simulado no modo 1 (noradrenalina fixa), com a PAM basal e as doses reais de Ang II de cada caso.
- **Efeito:** a diferença entre casos e controles, para comparação com o efeito do modelo. Como o modelo não
  tem braço placebo, a comparação foi feita pelo **efeito**, e não pela proporção de respondedores no braço
  tratado.
- **Análise de sensibilidade:** restrita a casos com PAM basal entre 55 e 70 mmHg, faixa de inclusão do
  ATHOS-3.

Limitações assumidas *a priori*:

- tamanho amostral pequeno e PAM esparsa;
- desenho não randomizado: a Ang II é usada como resgate;
- ausência de informação sobre uso crônico de BRA, o que impede testar o fator r;
- meta clínica diferente da do ensaio (65 × 75 mmHg).

### 2.6.7 Software e reprodutibilidade

A extração e as análises estatísticas foram feitas em Python (pandas, DuckDB e matplotlib) num caderno
Jupyter. Os testes dos níveis 1 a 3 e o problema inverso foram implementados em Julia, com as mesmas funções
do modelo usadas pelo aplicativo, o que garante que o modelo validado é o mesmo modelo simulado. Todas as
etapas são executadas por scripts, com semente aleatória fixa, a partir dos arquivos originais do MIMIC-IV.

---

## 3.3.6 Aba de validação do modelo

A sexta aba do aplicativo, **"Validação do modelo"** (Figura Z), reúne a comparação entre o modelo e os
pacientes reais do MIMIC-IV descrita na seção 2.6. Ela foi pensada para que o leitor veja, numa única tela,
o resumo do que foi validado e a comparação gráfica entre o modelo e os dados. A aba é dividida em um painel
à esquerda, com a tabela-resumo, e uma grade de seis gráficos à direita.

**Painel à esquerda.** No topo, um menu permite escolher a coorte de pacientes reais: **"Choque vasodilatador
(sepse)"**, que é a análise principal, ou **"Todos com noradrenalina"**, que é a análise de sensibilidade.
Abaixo do menu aparecem o número de internações da coorte selecionada e a tabela **"Resumo dos resultados"**.
Cada linha da tabela corresponde a um teste e tem cinco colunas:

- o **nível** de validação (0 a 4);
- **o que foi testado**, em linguagem simples;
- o valor do **modelo**;
- o valor dos **pacientes reais**: mediana, ou efeito com IC 95%; quando há dois números, o primeiro é do
  adulto e o segundo, do idoso;
- o **resultado**, num selo colorido: verde para "passa", amarelo para "parcial", vermelho para "não passa",
  cinza para "inconclusivo" e cinza-claro para "a fazer".

Os critérios de cada selo são os da Tabela Y e são recalculados automaticamente a partir dos arquivos de
resultado. Por exemplo, a PAM antes do tratamento recebe o selo "parcial" se o valor do modelo estiver dentro do
IIQ dos pacientes. O efeito de cada aumento de noradrenalina recebe "passa" se o valor do modelo estiver
dentro do IC 95% da diferença em diferenças.

A tabela usa sempre os parâmetros **padrão** do modelo e, por isso, não muda quando os controles deslizantes
são movidos: ela representa o resultado oficial da validação. Abaixo dela, notas explicam a convenção dos
valores (adulto / idoso), a legenda dos gráficos e a restrição de uso dos dados.

**Gráficos à direita.** Em todos os gráficos, os pacientes reais aparecem em branco e o modelo em azul. A linha
tracejada horizontal marca a meta de 65 mmHg.

- **Linha superior:**
  - **Adulto e Idoso, pressão antes da noradrenalina:** para PAS, PAD, PAM e pressão de pulso, uma barra
    cinza mostra o IIQ dos pacientes, um traço branco a mediana e um losango azul o valor do modelo. O
    subtítulo indica, para cada variável, se o modelo está dentro ("ok") ou fora do IIQ. Corresponde ao
    nível 1.
  - **Dose × PAM (após o início da noradrenalina):** a mediana e o IIQ da PAM dos pacientes por faixa de dose,
    comparados à curva dose-resposta do modelo. A linha é tracejada para o adulto e contínua para o idoso.
- **Linha inferior:**
  - **Adulto e Idoso, PAM desde o início da noradrenalina:** a PAM média dos pacientes (± erro-padrão)
    alinhada ao início da noradrenalina, de −60 a +240 min. São exibidas duas curvas do modelo, ambas
    recebendo a dose média real de noradrenalina: a contínua parte da PAM do próprio modelo; a tracejada
    parte da PAM real antes do tratamento e mostra apenas o efeito da noradrenalina.
  - **Dose média real de noradrenalina:** a dose média ao longo do tempo, que é a entrada do modelo nas
    curvas ao lado.

**Interação com o restante do aplicativo.** Os gráficos, ao contrário da tabela, são atualizados em tempo real
pelos controles deslizantes das abas 1 a 3: frequência cardíaca, débito cardíaco do idoso, fatores de idade
de R_p e C, fração do teto, EC50 e meia-vida da noradrenalina. Isso permite observar, por exemplo, que
alterar o fator de complacência muda a pressão de pulso, mas não a PAM, e que reduzir o débito cardíaco do
idoso aumenta o efeito máximo da noradrenalina. Esse ajuste manual até o modelo coincidir com os dados
equivale a uma calibração visual, e não a uma validação, o que é indicado na própria aba.

**Origem dos dados e privacidade.** A aba não acessa o MIMIC-IV diretamente. Ela lê apenas arquivos de
resumo agregados, gerados pelo script `resumo_mimic.jl` a partir dos resultados das análises, e cada
valor exibido corresponde a no mínimo 11 internações, em respeito ao termo de uso do PhysioNet. Se esses
arquivos não estiverem presentes, a aba exibe as instruções para gerá-los, e as demais abas funcionam
normalmente.

*Figura Z – Aba "Validação do modelo" do aplicativo, coorte de choque vasodilatador, com os parâmetros
padrão. À esquerda, a tabela-resumo da validação; à direita, a comparação entre pacientes reais do MIMIC-IV
(branco) e o modelo (azul).* (Imagem: `mimic completo/validacao_vasodilatador/figuras/app_aba6_validacao.png`.)
