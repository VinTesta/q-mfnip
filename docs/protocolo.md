# Protocolo experimental (CONGELADO em 2026-11-06, 09h40)

Status: **congelado**. Reescrito em 2026-11-05 para a nova direção do artigo (`docs/plano-artigo-entrega2.md`) e ajustado em 2026-11-06 pela decisão D1. Data de congelamento (passo P0 de `docs/passo-a-passo-entrega2.md`, antes de E1): **2026-11-06, 09h40**, com os padrões da D4. Qualquer mudança daqui em diante vai para §8 (desvios), com motivo.

## 0. Mudanças de escopo

### 0.1 Saída de QUBO, QA e QAOA (2026-11-05)
Este protocolo tratava da comparação entre quantum annealing, QAOA e métodos clássicos sobre uma formulação QUBO do MFNIP. **QUBO, QA e QAOA foram retirados do artigo**, e com eles:
- as hipóteses H1 (qualidade), H2 (tempo) e H3 (escala);
- os parâmetros Z, p e T da fronteira n\*.

O artigo agora estuda a **busca quântica de mínimo de Dürr–Høyer** aplicada ao MFNIP:
- a **interface** que permite executar o algoritmo no problema (codificação, preparação do estado e oráculo);
- a **vantagem teórica provada** sobre a busca exaustiva clássica;
- a **comparação com a busca exaustiva** na computação clássica.

O MILP continua como gabarito do ótimo e como contexto prático.

### 0.2 Espaço de busca viável (decisão D1, 2026-11-06)
- **Problema:** com orçamento não degenerado, as interdições que cabem no orçamento são menos que √(2^m) (m = 20: 222 contra 1.024). A busca exaustiva sobre 2^m seria um rival espantalho.
- **Decisão:** a busca, quântica e clássica, passa a ser sobre as interdições viáveis da **variante de cardinalidade**: custo unitário e até k arcos, F_k = {x : |x| ≤ k}, N = |F_k| = Σ_{i≤k} C(m, i).
- **Preparação:** o estado inicial uniforme sobre F_k é preparado com o circuito de Dicke.
- **Custos quaisquer:** ficam como limitação declarada.

Detalhes em `docs/plano-execucao-entrega2.md` §0.

## 1. Pergunta, proposição e hipóteses
**Pergunta:** qual vantagem um algoritmo quântico de busca oferece sobre a busca exaustiva clássica no MFNIP, a que custo de recursos, e como isso se situa frente ao estado prático clássico?

- **Proposição 1 (demonstrada).** Com N = |F_k|:
  - a busca de Dürr–Høyer, com a preparação A_k e o oráculo O_τ (ambos com poly(n, m) portas), encontra uma interdição ótima com probabilidade ≥ 1/2 usando O(√N) aplicações de A_k e O_τ;
  - uma busca clássica que só acessa os fluxos por avaliação precisa de Ω(N) avaliações no pior caso.
- **H4 (escala, simulação).** O custo médio (consultas ao oráculo + avaliações clássicas) até medir o ótimo cresce como N^β com β ∈ [0,4; 0,6]. A busca clássica em ordem aleatória sobre F_k cresce com expoente próximo de 1.
- **H5 (hardware IBM).** Numa instância com m = 3, k = 1 e ótimo único, a frequência da interdição ótima medida após o número ideal de iterações é significativamente maior que 1/N.
- **Caracterização:** qubits, portas de dois qubits e profundidade da preparação de Dicke e das realizações do oráculo, em função de m e n.

## 2. Parâmetros e critérios de refutação
Os valores abaixo são os padrões da decisão D4, adotados no congelamento (o usuário mandou seguir o roteiro sem alterá-los).
- **Intervalo de β (H4):** [0,4; 0,6].
- **Nível de significância (H5):** 0,05, teste binomial unilateral.
- **H4 refutada se:** o β ajustado, com IC 95% por *bootstrap* sobre instâncias, ficar fora do intervalo.
- **H5 refutada se:** a frequência do ótimo no hardware não for significativamente maior que 1/N.

## 3. Instâncias
- Famílias de `src/qmfnip/instances.py`, com sementes fixas e hash do conteúdo.
- **Custo unitário e orçamento k < κ** (κ = custo do corte que zera o fluxo). Isso garante ótimo maior que zero; a degenerescência no outro extremo (ótimo igual ao fluxo original) é conferida em cada instância.
- **H4 (E1):**
  - família em camadas, larguras w = 2 a 5 (κ = w), k = 1 a w − 1, sementes 0, 1 e 2;
  - são 30 instâncias, com N = |F_k| de 9 a ~971 mil.

  | w | m | k = 1 | k = 2 | k = 3 | k = 4 |
  |---|---|---|---|---|---|
  | 2 | 8 | 9 | — | — | — |
  | 3 | 24 | 25 | 301 | — | — |
  | 4 | 44 | 45 | 991 | 14.235 | — |
  | 5 | 70 | 71 | 2.486 | 57.226 | ~971.000 |

- **H5 (E3):** m = 3, k = 1, κ ≥ 2, ótimo único (M = 1), escolhida automaticamente entre instâncias pequenas do gerador.

## 4. Métodos
| Método | Papel | Plataforma |
|---|---|---|
| Dürr–Høyer, vetor de estado completo | Validação do simulador reduzido | numpy, N ≤ 2^14 |
| Dürr–Høyer, simulador reduzido (plano de dois estados) | Escala (H4) | numpy, N até ~10⁶ |
| Grover com preparação de Dicke e oráculo de tabela-verdade | Demonstração (H5), variante "interface" (N = 4) | Qiskit: simulador ideal, `FakeFez`, hardware IBM |
| Grover com H^⊗m e oráculo de tabela-verdade | Demonstração (H5), variante "hipercubo" (N = 8) | Idem |
| Enumeração determinística de F_k | Rival da Proposição 1 (certifica com N avaliações) | Clássico |
| Busca clássica em ordem aleatória sobre F_k | Rival com a mesma garantia probabilística (H4) | Clássico |
| MILP (HiGHS) | Gabarito do ótimo e contexto prático | Clássico |

## 5. Métricas
- **Custo:** consultas ao oráculo (cada iteração de Grover = 1) mais avaliações clássicas (cada candidato conferido = 1), até medir o ótimo pela primeira vez.
- **Expoente β** da regressão log-log contra N e contra N/M, com IC 95%.
- **Probabilidade de acerto** dentro do orçamento teórico de consultas de Dürr–Høyer (22,5√N + 1,4 log₂²N; constante a conferir no artigo original).
- **Recursos:** qubits lógicos, portas de dois qubits e profundidade, lógicos e após transpilação para o `FakeFez`.
- **Hardware:** frequência de cada interdição medida, p-valor do teste binomial, dispositivo, data, profundidade transpilada, tempo de QPU e de fila, id do job.
- **Contexto:** tempo do MILP e da enumeração nas instâncias de E1; estudo de escala do notebook `01`.

## 6. Repetições
- Execuções por instância e método em E1 (R): 200 (padrão D4).
- *Shots* no hardware: 4.096 por circuito (padrão D4).
- Sementes derivadas e registradas em todas as execuções.

## 7. Protocolo de hardware
1. Todo circuito roda primeiro no simulador ideal e depois no `FakeFez` (com ruído).
2. Só vai para o hardware IBM se o simulador ideal reproduzir a teoria (cada frequência a até 3 erros-padrão) e se `allow_hardware=True` for liberado explicitamente.
3. O id do job é gravado em `outputs/` antes de esperar o resultado.
4. Registrar: dispositivo, data, versão do SDK, número de iterações, *shots*, profundidade e portas de dois qubits após transpilação, tempos de QPU e de fila.

## 8. Desvios do protocolo
(registrar aqui qualquer mudança pós-congelamento, com motivo)
