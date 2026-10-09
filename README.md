# dsh-paper-doc-adapter — Parsed exam paper structural self-consistency check across question type, answer, score and yotta identifier

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-paper-doc-adapter` reads one parsed exam paper — the paper header plus one row per question — and checks that parse result's own structural self-consistency: that each question records its number and stem, that an answer or an explanation is present, that the question scores total the paper score the header states, that the question type comes from the vocabulary you configure, that the difficulty coefficient falls inside your range, that question identifiers are present and unique, that a knowledge point is recorded, and that no template placeholder survives in the stem.

## What it looks like

![Terminal demo of dsh-paper-doc-adapter: real output over its PD-006 fixture](https://raw.githubusercontent.com/PerryLink/dsh-paper-doc-adapter/main/docs/assets/dsh-paper-doc-adapter-demo.png)

Real output from this plugin over its own `PD-006` test fixture — not a mock-up. The rule pack ships no invented quotations, so a finding names both the clause it applied and the fact that the clause text was not obtained.

## What it answers

| You ask | What it answers |
|---|---|
| Both the question number and the stem are blank on a row — does the check say anything? | Yes. `PD-001` reports a row whose `questionNo` and `stem` are both empty, because it asks for at least one of the two. It checks that something is filled, not whether the question is well written or the stem rigorous. |
| A question has its number and stem, but neither an answer nor an explanation. | `PD-002` reports that row: it asks for at least one of `answer` and `explanation`. It does not check whether the answer is correct — that is subject-expert review, and the pack says as much. |
| The question scores add up to 98 while the header says 100 — is that caught? | Yes. `PD-003` adds the `score` column and compares the total with the `totalScore` the paper header states, allowing the configured tolerance of 0.01; if the header total is not a parseable number it reports itself in `skipped` instead. It only does the addition — whether the marks are distributed sensibly is not judged. |
| We never listed our own question types. What does the tool do with the question type column? | `PD-004` reports itself in `skipped`, because its `values` list ships empty: naming question types is your institution's convention and the engine hard-codes no list. Once you configure your values, a `questionType` outside them is reported; the rule then checks membership only, and it performs no question-type-specific structure check. |
| The difficulty column holds `1.2` in one row and `中等` in another — what comes back? | `PD-005` reports the value it cannot parse as a number and the value outside the configured `min`/`max` range of 0–1. That range is your institution's convention, not the only scale — 1–5 or a percentage needs `min`/`max` changed or the rule disabled. It checks the range only, never whether the difficulty is appropriate, and it is capped at `info`. |
| Two questions carry the same yotta identifier. Why is that worse than a blank one? | `PD-006` reports the repeated value, comparing with whitespace ignored, because importing that parse result would silently overwrite an existing question; a blank identifier only keeps that one question out. With no identifier filled anywhere the rule reports itself in `skipped`. It checks presence and uniqueness, and nothing beyond that. |

## Standards it follows

| Document | Number | Cited by rules |
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
dsh plugin --profile <name> add dsh-paper-doc-adapter
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
