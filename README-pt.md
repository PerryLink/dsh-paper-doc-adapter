# dsh-paper-doc-adapter — Verificação da coerência estrutural de um exame analisado: tipo de questão, resposta, pontuação e identificador yotta

`dsh-paper-doc-adapter` lê um exame já analisado —o cabeçalho do exame mais uma linha por questão— e verifica a coerência estrutural interna desse resultado: se cada questão regista o seu número e o seu enunciado, se há uma resposta ou uma explicação, se a soma das pontuações das questões coincide com a pontuação total indicada no cabeçalho, se o tipo de questão vem do vocabulário que você configura, se o coeficiente de dificuldade fica dentro do seu intervalo, se os identificadores de questão estão presentes e não se repetem, se um ponto de conhecimento está registado e se não resta nenhum marcador de modelo no enunciado.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Numa linha estão vazios tanto o número como o enunciado — isso é reportado? | Sim. `PD-001` reporta a linha cujo `questionNo` e `stem` estão ambos vazios, porque exige que pelo menos um dos dois seja preenchido. Verifica que algo está preenchido, não se a questão está bem redigida ou o enunciado é rigoroso. |
| Uma questão tem número e enunciado, mas nem resposta nem explicação. | `PD-002` reporta essa linha: exige pelo menos um de `answer` e `explanation`. Não verifica se a resposta está correta — isso é revisão de um especialista da matéria, e o próprio pacote o diz. |
| As pontuações somam 98 e o cabeçalho diz 100 — isso é detetado? | Sim. `PD-003` soma a coluna `score` e compara o total com o `totalScore` indicado no cabeçalho do exame, com a tolerância configurada de 0.01; se o total do cabeçalho não for um número analisável, reporta em `skipped` que não pôde ser executada. Faz apenas a soma: não julga se a distribuição dos pontos é razoável. |
| Nunca declarámos os nossos próprios tipos de questão. O que a ferramenta faz com essa coluna? | `PD-004` reporta em `skipped` que não pôde ser executada, porque a sua lista `values` vem vazia: nomear os tipos de questão é convenção da sua instituição e o motor não codifica nenhuma lista. Ao configurar os seus valores, um `questionType` fora deles é reportado; a regra passa então a verificar apenas a pertença e não faz nenhuma validação estrutural por tipo de questão. |
| A coluna da dificuldade traz `1.2` numa linha e `中等` noutra — o que devolve? | `PD-005` reporta o valor que não consegue analisar como número e o que fica fora do intervalo `min`/`max` configurado, 0–1. Esse intervalo é convenção da sua instituição, não a única escala: com 1–5 ou percentagens é preciso alterar `min`/`max` ou desativar a regra. Verifica apenas o intervalo, nunca se a dificuldade é adequada, e está limitada a `info`. |
| Duas questões trazem o mesmo identificador yotta. Porque é pior do que um vazio? | `PD-006` reporta o valor repetido, comparando sem espaços, porque importar esse resultado sobrescreveria silenciosamente uma questão existente; um identificador vazio apenas deixa essa questão de fora. Se nenhuma linha trouxer identificador, a regra reporta em `skipped` que não pôde ser executada. Verifica presença e unicidade, e nada além disso. |

## Normas que segue

| Documento | Número | Regras que o citam |
|---|---|---|
| 《试题元数据规范》 | JY/T 0606 系列（本次未取得条文） | PD-001, PD-002, PD-003, PD-006, PD-007, PD-008 |
| 本机构题库与命题口径（本机构配置） | 无统一标准（本条依据为本机构配置的题型口径） | PD-004 |
| 本机构题库与命题口径（本机构配置） | 无统一标准（本条依据为本机构配置的难度口径） | PD-005 |

**Boundary:** this plugin checks a **试卷解析结果** for structural self-consistency — that each question records its
number and stem, that an answer or an explanation is present, that the question scores total the paper's score,
that the question type comes from your vocabulary, that the difficulty coefficient falls inside your range, that
question identifiers are present and unique, that a knowledge point is recorded, and that no placeholder survives.
It does **not** decide whether a question is well written, whether an answer is correct, whether the difficulty is
appropriate, or whether the paper meets its assessment objectives.

> ### ⚠️ What this plugin deliberately does not do
>
> **It treats the paper as a generic table and performs no question-type-specific checking.** So it **does not
> verify that an answer letter falls within the options offered**, that a fill-in-the-blank has the right number of
> blanks, or that a multiple-choice question has exactly one correct option. Those need the structure of each
> question type parsed, which this adapter does not attempt. That boundary is stated in the pack's header and in
> the troubleshooting section.
>
> **It never checks whether data is fit to import into a question bank beyond key presence and uniqueness.** A
> duplicate identifier is the dangerous case — importing would silently overwrite an existing question — which is
> why `PD-006` is `warn` and why it reports itself in `skipped` when no identifier column is present rather than
> checking the wrong column.
>
> **The difficulty range `0–1` is a local convention, not the only scale.** It is the common convention, larger
> meaning easier; a unit using 1–5 or a percentage can change `min`/`max` or disable the rule.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained** — the
> verification pass retrieved neither JY/T 0606's text nor the yotta platform's field specification. When the
> texts are in hand, replace each `excerpt` with the real clause and raise `kind` to `direct`.

## Compatibility

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-paper-doc-adapter
dsh --profile <name> --dump-config | grep 'dsh-paper-doc-adapter'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/paper-doc-adapter.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-paper-doc-adapter
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-paper-doc-adapter contributors.
