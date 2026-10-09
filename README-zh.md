# dsh-paper-doc-adapter — 试卷解析结构核对

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-paper-doc-adapter` 读取一份试卷解析结果——试卷表头加每道题一行——核对这份解析结果自身的结构自洽：每道题是否填写了题号与题干、是否填写了答案或解析、各题分值合计是否等于表头写的试卷总分、题型取值是否出自你配置的口径、难度系数是否落在你配置的范围内、题目标识是否齐备且唯一、是否标注了知识点、题干栏是否残留模板占位符。

## 实际输出长什么样

![Terminal demo of dsh-paper-doc-adapter: real output over its PD-006 fixture](https://raw.githubusercontent.com/PerryLink/dsh-paper-doc-adapter/main/docs/assets/dsh-paper-doc-adapter-demo.png)

本插件对自己 `PD-006` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 某行的题号与题干都是空的，会被报出吗？ | 会。`PD-001` 只要求 `questionNo` 与 `stem` 至少填一项，两项都空才报出该行。它只核对是否填写，不判断题目出得好不好、题干是否严谨。 |
| 一道题有题号和题干，但答案与解析都没有。 | `PD-002` 会报出该行：它要求 `answer` 与 `explanation` 至少填一项。它不核对答案是否正确——那需要学科专家审题，规则库自己也这么写明。 |
| 各题分值加总为 98，表头写的是 100，能查出来吗？ | 能。`PD-003` 把 `score` 栏加总，与试卷表头写的 `totalScore` 相比，允许配置的 0.01 偏差；表头总分不是可解析的数字时，本条报告自己进入 `skipped`，而不是静默通过。它只做加法核对，不判断分值分配是否合理。 |
| 我们还没有配置自己的题型口径，工具会怎么处理题型栏？ | `PD-004` 会报告自己进入 `skipped`：它的 `values` 出厂为空，题型命名属你所在机构的口径，引擎不硬编码任何清单。配置了取值以后，不在册的 `questionType` 会被报出；此时本条只核对是否在册，也不针对题型做结构校验。 |
| 难度栏一行写 `1.2`，一行写 `中等`，会返回什么？ | `PD-005` 会把无法解析为数字的值报出，也会把落在配置范围 0–1 之外的值报出。0–1 是本机构口径、不是唯一刻度——用 1–5 或百分制就改 `min`/`max` 或停用本条。它只核对范围，不判断难度是否恰当，且封顶 `info`。 |
| 两道题用了同一个 yotta 标识，为什么这比空着更糟？ | `PD-006` 会报出重复的值（比较时忽略空白字符），因为导入这份解析结果会静默覆盖已有题目；空标识只是这道题入不了库。整栏都没填时，本条报告自己进入 `skipped`。它只核对齐备与唯一，此外不作判断。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
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

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-paper-doc-adapter
dsh --profile <name> --dump-config | grep 'dsh-paper-doc-adapter'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/paper-doc-adapter.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-paper-doc-adapter
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-paper-doc-adapter contributors.
