# dsh-paper-doc-adapter

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
pnpm pack
dsh plugin --profile <name> add ./*.tgz
dsh --profile <name> --dump-config | grep 'dsh-paper-doc-adapter'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`. As chaves e os parâmetros de cada regra estão em [README.md](README.md#configuration) (versão principal em inglês).

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
