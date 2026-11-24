# Glossário de siglas e termos

Siglas e termos usados no código, no notebook, no documento de metodologia e nos resultados.
Vai do mais básico ao mais específico. Os nomes em `código` são os usados nos arquivos.

---

## 1. Pressão e circulação (o básico)

| Sigla | Significado | Unidade | O que é, em uma frase |
|---|---|---|---|
| **PA** | Pressão arterial | mmHg | Pressão do sangue dentro das artérias; oscila a cada batimento. |
| **PAS** | Pressão arterial sistólica | mmHg | O pico da pressão, logo depois de o coração ejetar ("a máxima", ex.: 120 em 120/80). |
| **PAD** | Pressão arterial diastólica | mmHg | O vale da pressão, no fim do relaxamento do coração ("a mínima", ex.: 80). |
| **PAM** | Pressão arterial média | mmHg | Média da pressão ao longo do batimento. É a pressão que perfunde os órgãos; a meta no choque é **PAM ≥ 65**. Na prática clínica, PAM ≈ PAD + PP/3. |
| **PP** | Pressão de pulso | mmHg | PAS − PAD. Cresce quando as artérias ficam rígidas (idosos). |
| **FC** | Frequência cardíaca | bpm (batimentos/min) | Quantas vezes o coração bate por minuto. |
| **VS** | Volume sistólico | ml | Volume de sangue ejetado em cada batimento. |
| **DC** | Débito cardíaco | L/min | Volume bombeado por minuto: DC = VS × FC. |
| **PVC** | Pressão venosa central | mmHg | Pressão nas grandes veias, perto do coração. O modelo usa 0 (`P_VEN`). |
| **RVS** | Resistência vascular sistêmica | dyn·s·cm⁻⁵ | "Aperto" dos vasos: RVS = 80 × (PAM − PVC) / DC. Normal ≈ 900–1300; no choque vasodilatador fica baixa. |
| **mmHg** | Milímetros de mercúrio | — | Unidade de pressão usada na clínica. |

## 2. Choque e terapia intensiva

| Sigla / termo | Significado |
|---|---|
| **Choque** | Falência circulatória: a pressão não basta para levar oxigênio aos órgãos. |
| **Choque vasodilatador** | Choque em que os vasos "abrem demais" (RVS baixa). A causa mais comum é a sepse. É o que o modelo representa. |
| **Choque refratário** | Choque que não responde a doses altas de vasopressor (aqui: noradrenalina > 0,2 µg/kg/min sem atingir a meta). |
| **Choque cardiogênico** | Choque por falha do coração (DC baixo). **Não** é o que o modelo representa. |
| **Choque hipovolêmico** | Choque por perda de volume (hemorragia, desidratação). Também não é representado. |
| **Sepse / choque séptico** | Resposta desregulada à infecção / sepse com choque. |
| **UTI** (*ICU*) | Unidade de terapia intensiva. |
| **MICU, SICU, TSICU** | UTI clínica, cirúrgica e de trauma (nomes do MIMIC). |
| **CVICU, CCU** | UTI cardiovascular (pós-cirurgia cardíaca) e unidade coronariana. Saem da coorte "vasodilatador". |
| **Vasopressor** | Remédio que contrai os vasos e sobe a PA. |
| **NE / nora** | Noradrenalina (norepinefrina): o vasopressor de primeira linha. Dose em **µg/kg/min**. |
| **Ang II** | Angiotensina II (nome comercial Giapreza): vasopressor de resgate no choque refratário. Dose em **ng/kg/min**. |
| **Vasopressina, adrenalina, fenilefrina, dopamina** | Outros vasopressores. O modelo não os representa; a PAM medida enquanto eles correm é descartada. |
| **SRAA** (*RAAS*) | Sistema renina-angiotensina-aldosterona: o sistema hormonal da Ang II. |
| **IECA** | Inibidor da enzima conversora de angiotensina (ex.: enalapril). Remédio de pressão. |
| **BRA** | Bloqueador do receptor de angiotensina (ex.: losartana). Atenua o efeito da Ang II. |
| **SSC** | *Surviving Sepsis Campaign*: diretriz internacional de sepse (de onde vem a meta PAM ≥ 65). |
| **ATHOS-3** | Ensaio clínico da Ang II no choque vasodilatador (Khanna et al., NEJM 2017). Meta PAM 75; 69,9% responderam contra 23,4% no placebo. |
| **Swan-Ganz, PiCCO, NICOM** | Monitores que medem o DC à beira do leito (termodiluição, contínuo e não invasivo). São raros no MIMIC. |
| **CCO** | *Continuous cardiac output*: DC contínuo (monitor Swan-Ganz). |

## 3. O modelo (Windkessel e farmacologia)

| Sigla / símbolo | Nome no código | Significado | Unidade |
|---|---|---|---|
| **WK3** | — | Windkessel de 3 elementos: modelo "elétrico" da circulação, com resistência, complacência e impedância. | — |
| **0D** | — | Modelo concentrado: sem geometria, só tempo (não simula a onda percorrendo a artéria). | — |
| **R_p** | `Rp` | Resistência periférica: o "aperto" dos pequenos vasos. É onde os vasopressores agem. | mmHg·s/ml |
| **C** | `C` | Complacência arterial: quanto as artérias "esticam". Cai com a idade e define a PP. | ml/mmHg |
| **Z_c** | `zc(Rp)` | Impedância característica da aorta; no modelo, 6% de R_p (`RAZAO_ZC`). | mmHg·s/ml |
| **P_c** | `Pc` | Pressão no "capacitor" (as artérias complacentes). | mmHg |
| **P_ao** | `pao` | Pressão na aorta = P_c + Z_c × Q_in. É a PA que o modelo devolve. | mmHg |
| **Q_in** | `q_in` | Fluxo que sai do coração: meia senoide durante a ejeção. | ml/s |
| **T_ej** | `t_ejecao(FC)` | Tempo de ejeção, que encurta com a FC (Weissler 1968). | s |
| **τ = R_p × C** | — | Constante de tempo do Windkessel: quão rápido a pressão cai na diástole. | s |
| **Euler** | `DT_EULER` | Método numérico que avança a equação em passos pequenos (0,1 ms). | — |
| **Quase-estática** | `pam_com_aii` | Atalho: como os remédios agem em minutos e o coração em segundos, a PAM é calculada direto, sem simular cada batimento. | — |
| `fRp`, `fC` | `FATOR_RP_IDADE`, `FATOR_C_IDADE` | Fatores de envelhecimento: o idoso tem R_p × 1,15 e C × 0,5. | — |
| **PK** | — | Farmacocinética: o que o corpo faz com o remédio (quanto dele está agindo ao longo do tempo). | — |
| **PD** | — | Farmacodinâmica: o que o remédio faz com o corpo (quanto sobe R_p). | — |
| **t½** | `T_MEIA_AII`, `T12_NE` | Meia-vida: tempo para o efeito cair à metade. Ang II ≈ 1 min; nora 2 a 6,8 min. | min |
| **x** | `x` | Dose efetiva: a dose "que está agindo", atrasada pela PK em relação à dose infundida. | igual à dose |
| **Hill** | `hill(x, Emax, EC50)` | Curva dose-efeito em S: E = Emax·x / (EC50 + x). | — |
| **Emax** | `Emax`, `EmaxN` | Efeito máximo do remédio (fração de aumento de R_p; 0,5 = +50%). | — |
| **EC50** | `ec50_aii`, `ec50_ne` | Dose que dá metade do efeito máximo. | dose |
| **r (Schild)** | `r_bra` | Quanto o BRA "desloca" a curva da Ang II para a direita (precisa de r vezes mais dose). | — |
| **F15** | `F15` | Fração do caminho até a meta já percorrida em 15 min; identifica cedo quem não responde. | — |
| **Teto do critério 4** | `teto_ne` | Maior Emax da nora compatível com "nora sozinha não chega a 65" no refratário (≈ 0,046). | — |
| **Titulação** | `titular`, `troca` | Regra que ajusta a dose a cada 5 min conforme a PAM (como a enfermagem faz). | — |

## 4. Dados (MIMIC-IV)

| Termo | Significado |
|---|---|
| **MIMIC-IV** | Banco público (com credenciamento) de prontuários de UTI do Beth Israel Deaconess, Boston. A versão *demo* tem 100 pacientes; a completa, cerca de 300 mil. |
| **subject_id** | Identificador do **paciente**. |
| **hadm_id** | Identificador da **internação hospitalar**. |
| **stay_id** | Identificador da **passagem pela UTI** (uma internação pode ter várias). |
| **itemid** | Código de cada tipo de medida ou remédio (ex.: 220052 = PAM invasiva; 221906 = noradrenalina). Os nomes estão em `d_items`. |
| **chartevents** | Tabela dos sinais vitais (PA, FC, DC...). A maior de todas (~430 milhões de linhas). |
| **inputevents** | Tabela das infusões (doses de remédios com início e fim). |
| **prescriptions** | Prescrições do hospital (usada para IECA/BRA). |
| **diagnoses_icd** | Diagnósticos de cada internação. |
| **CID** (*ICD*) | Classificação Internacional de Doenças (versões 9 e 10). Ex.: R65.21 = choque séptico. |
| **Invasiva / não invasiva** | PA por cateter dentro da artéria (contínua, mais confiável) ou por manguito (intermitente). |
| **anchor_age / anchor_year** | Idade e ano "deslocados" que o MIMIC usa para anonimizar; a idade real é calculada a partir deles. |
| **refratario_proxy** | Definição operacional usada aqui: ≥ 6 h com nora ≥ 0,2 µg/kg/min. Não é diagnóstico clínico. |
| **Início incidente** | A nora começou na UTI ≥ 60 min após a entrada, então existe PAM "antes da nora". |
| **Coorte** | Grupo de pacientes analisado ("todos" ou "vasodilatador"). |
| **CSV / .csv.gz** | Tabela em texto / a mesma tabela compactada. |
| **Parquet** | Formato de tabela compacto e rápido (o chartevents foi de 2,5 GB para 71 MB). |
| **DuckDB** | Programa que consulta arquivos enormes com SQL sem carregá-los inteiros na memória. |

## 5. Validação e estatística

| Termo | Significado |
|---|---|
| **Verificação** | O código resolve as equações certas? (`verificar.jl`, nível 0) |
| **Validação** | As equações certas descrevem pacientes reais? (níveis 1 a 4) |
| **Calibração** | Ajustar parâmetros para o modelo bater com um dado. Não se valida com o mesmo dado usado para calibrar. |
| **Malha aberta** | O modelo recebe a dose real do paciente (não a do controlador do app) e prevê a PAM. |
| **Mediana / IIQ** | Valor do meio / intervalo interquartil (do 25º ao 75º percentil): onde está a metade central dos pacientes. |
| **Viés** | Erro médio (modelo − medido). Negativo = o modelo subestima. |
| **MAE** | Erro absoluto médio: em média, quantos mmHg o modelo erra. |
| **RMSE** | Raiz do erro quadrático médio: como o MAE, mas pune mais os erros grandes. |
| **% \|e\| ≤ 10** | Fração das previsões que erram no máximo 10 mmHg. |
| **Referência simples** | Previsão "sem modelo": a PAM fica igual à de antes, ou é igual à média da população. O modelo tem de ganhar delas. |
| **Habilidade** (*skill*) | 1 − RMSE do modelo / RMSE da melhor referência. Maior que 0 = o modelo acrescenta informação. |
| **Validação cruzada por paciente** | Ajusta em parte dos pacientes e testa nos outros; todas as internações de um paciente ficam do mesmo lado. |
| **Bland-Altman** | Gráfico do erro contra o valor médio, com o viés e os limites de concordância (± 1,96 desvios-padrão). |
| **CCC de Lin** | Coeficiente de concordância: 1 = modelo e medida idênticos. |
| **Viés de indicação** | Em dados observacionais, a dose sobe *porque* a PAM caiu; isso esconde o efeito real do remédio. |
| **Problema inverso / identificação** | Calcular, a partir da pressão medida, quais R_p e C o paciente teria (`planta_individual.jl`). |
| **Coorte virtual** | Pacientes simulados com parâmetros sorteados, para comparar com um ensaio clínico (nível 4). |
