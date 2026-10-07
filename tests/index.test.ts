import { describeTablePlugin } from './table-plugin-suite.ts'
import { Config } from '../src/config.ts'
import { parseMaterial, runCheck, SPEC } from '../src/model.ts'
import { buildView } from '../src/view.ts'
import { inject, name, resolvePackageFile, TOOL_NAME } from '../src/index.ts'

describeTablePlugin({
  name,
  inject,
  TOOL_NAME,
  resolvePackageFile,
  Config,
  rulesFile: 'rules/paper-doc-adapter.yaml',
  parseMaterial,
  runCheck,
  buildView,
  columnNames: SPEC.columns,
  samples: {
    good: {
          "paperTitle": "某某科目 2026 年模拟试卷",
          "subject": "某某科目",
          "grade": "高二",
          "paperVersion": "2026 版",
          "totalScore": "3",
          "durationMin": "90",
          "rows": [
                {
                      "序号": "1",
                      "题号": "1",
                      "题型": "单选题",
                      "题干": "下列关于……的说法，正确的是（　　）",
                      "选项": "A. ……；B. ……；C. ……；D. ……",
                      "答案": "B",
                      "解析": "本题考查……，依据……，故 B 正确。",
                      "分值": "3",
                      "难度": "0.72",
                      "知识点": "某某章节 某某知识点",
                      "来源": "2026 年某某模拟卷",
                      "题目ID": "YOTTA-2026-0001",
                      "标签": "基础题"
                }
          ]
    },
    unknownColumn: { rows: [{ 备注: '甲' }] },
  },
})
