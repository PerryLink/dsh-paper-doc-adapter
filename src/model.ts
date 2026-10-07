/**
 * dsh-paper-doc-adapter — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'paper_doc_adapter'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  /**
   * The question number.
   *
   * Deliberately **not** aliased to 序号: the reader treats that column as the row's own
   * display number, so mapping it here as well would make every row resolve its question
   * number to its position — hiding a blank 题号 cell behind the row counter. A register
   * that numbers its questions in the 序号 column can say so by adding `questionNo` to
   * that column instead.
   */
  questionNo: ['题号', '题目编号', 'questionNo'],
  questionType: ['题型', '题目类型', '类型', 'questionType'],
  stem: ['题干', '题目内容', '试题内容', 'stem'],
  options: ['选项', '备选项', '选择项', 'options'],
  answer: ['答案', '参考答案', '标准答案', 'answer'],
  explanation: ['解析', '试题解析', '说明', 'explanation'],
  score: ['分值', '本题分值', '满分', 'score'],
  difficulty: ['难度', '难度系数', '预计难度', 'difficulty'],
  knowledge: ['知识点', '考点', '所属章节', 'knowledge'],
  source: ['来源', '题目来源', '出处', 'source'],
  yottaId: ['题目ID', 'yotta ID', '标识', 'yottaId'],
  tags: ['标签', '题目标签', '分类标签', 'tags'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'questions', '题目'],
  columns: COLUMNS,
  header: {
  paperTitle: ['paperTitle', '试卷名称', '试卷标题'],
  subject: ['subject', '科目', '课程'],
  grade: ['grade', '年级', '学段'],
  paperVersion: ['paperVersion', '试卷版本', '版本'],
  totalScore: ['totalScore', '试卷总分', '总分'],
  durationMin: ['durationMin', '考试时长', '时长'],
  compiler: ['compiler', '命题人', '编制人'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '题干',
  'stem',
  '答案',
  'answer',
  '题号',
  'questionNo',
  '题型',
  'questionType',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
