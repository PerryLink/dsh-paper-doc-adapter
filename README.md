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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a full paper use `ptc` |

## What it does

Registers the `paper_doc_adapter` tool. It reads one parsed paper — the paper header plus one row per question —
applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `PD-001` | the question number and stem are recorded | warn | principle |
| `PD-002` | an answer or an explanation is present | warn | principle |
| `PD-003` | the question scores total the paper score | warn | principle |
| `PD-004` | the question type comes from your vocabulary (off by default) | info | local |
| `PD-005` | the difficulty coefficient is inside your range | info | local |
| `PD-006` | question identifiers are present and unique | warn | principle |
| `PD-007` | a knowledge point is recorded | warn | principle |
| `PD-008` | the stem holds no unreplaced placeholder | warn | principle |

## Install

```sh
pnpm pack
dsh plugin --profile <name> add ./dsh-paper-doc-adapter-0.1.0.tgz
dsh --profile <name> --dump-config | grep 'dsh-paper-doc-adapter'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/paper-doc-adapter.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `PD-003` `field` / `headerField` / `tolerance` — the score column and the header total it must match.
- `PD-004` `values` — your question types, e.g.
  `[单选题, 多选题, 判断题, 填空题, 简答题, 计算题, 作文题]`. Empty means no check.
- `PD-005` `min` / `max` — the difficulty range, `0` to `1` by default. **A local convention**, not a standard
  figure.
- `PD-008` `terms` — the placeholders to look for.

## Material format

The tool accepts JSON or YAML:

```yaml
paperTitle: 某某科目 2026 年模拟试卷
subject: 某某科目
grade: 高二
paperVersion: 2026 版
totalScore: '3'
durationMin: '90'
rows:
  - { 序号: '1', 题号: '1', 题型: 单选题, 题干: 下列关于……的说法，正确的是（　　）,
      选项: A. ……；B. ……；C. ……；D. ……, 答案: B,
      解析: 本题考查……，依据……，故 B 正确。, 分值: '3', 难度: '0.72',
      知识点: 某某章节 某某知识点, 题目ID: YOTTA-2026-0001, 标签: 基础题 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the paper's own column
names are kept, so a finding names the column it read. Note that 序号 is read as the row's display number — give
the question number its own column (题号).

## Rule sources

Rule data lives in `rules/paper-doc-adapter.yaml`. Its header explains what the plugin does not check, and each
rule's `note` repeats the part that matters for that rule. The load-time guard still requires a document, clause,
excerpt and source per rule, and still forbids a locally configured check from being `error`.

## Troubleshooting

- **It did not notice that an answer letter is outside the options.** By design: the plugin treats the paper as a
  generic table and performs no question-type-specific validation.
- **`PD-006` reports itself as skipped.** No identifier column is present, so the uniqueness check has nothing to
  key on. It reports that rather than checking the wrong column.
- **`PD-005` fires on a difficulty of `1.8`.** The default range is `0`–`1`; change `min`/`max` if your bank uses
  another scale.
- **`PD-003` fires although the paper adds up.** The header total and the sum of the rows disagree — usually a
  missing question or a mistyped score.
- **`PD-004` never runs.** Its vocabulary is empty; fill it with your bank's question types.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-paper-doc-adapter@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-paper-doc-adapter   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and the
check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-paper-doc-adapter contributors.
