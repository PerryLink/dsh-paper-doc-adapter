# dsh-paper-doc-adapter — विश्लेषित प्रश्नपत्र की संरचनात्मक संगति की जाँच: प्रश्न-प्रकार, उत्तर, अंक और yotta पहचानकर्ता

`dsh-paper-doc-adapter` एक विश्लेषित प्रश्नपत्र पढ़ता है — प्रश्नपत्र का हेडर और प्रत्येक प्रश्न की एक पंक्ति — और उसी विश्लेषण-परिणाम की आंतरिक संरचनात्मक संगति जाँचता है: क्या प्रत्येक प्रश्न में उसका क्रमांक और प्रश्न-कथन दर्ज है, क्या उत्तर या व्याख्या में से कम से कम एक दर्ज है, क्या सभी प्रश्नों के अंकों का जोड़ हेडर में लिखे कुल अंक के बराबर है, क्या प्रश्न-प्रकार आपके द्वारा कॉन्फ़िगर की गई सूची से आता है, क्या कठिनाई-गुणांक आपकी निर्धारित सीमा के भीतर है, क्या प्रश्न-पहचानकर्ता दर्ज और अद्वितीय हैं, क्या ज्ञान-बिंदु दर्ज है, और क्या प्रश्न-कथन में कोई टेम्पलेट प्लेसहोल्डर शेष नहीं है।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| किसी पंक्ति में प्रश्न-क्रमांक और प्रश्न-कथन दोनों खाली हैं — क्या कुछ बताया जाता है? | हाँ। `PD-001` उस पंक्ति को दर्ज करता है जिसमें `questionNo` और `stem` दोनों खाली हैं, क्योंकि वह दोनों में से कम से कम एक भरा होने की अपेक्षा करता है। यह देखता है कि कुछ भरा है, यह नहीं कि प्रश्न अच्छा है या कथन कठोर है। |
| एक प्रश्न में क्रमांक और कथन हैं, पर न उत्तर है न व्याख्या। | `PD-002` उस पंक्ति को दर्ज करता है: वह `answer` और `explanation` में से कम से कम एक की अपेक्षा करता है। यह नहीं जाँचता कि उत्तर सही है — वह विषय-विशेषज्ञ की समीक्षा है, और नियम-संग्रह स्वयं यही कहता है। |
| प्रश्नों के अंक जोड़कर 98 बनते हैं और हेडर में 100 लिखा है — क्या यह पकड़ में आता है? | हाँ। `PD-003` `score` कॉलम का जोड़ करता है और उसकी तुलना प्रश्नपत्र के हेडर में लिखे `totalScore` से करता है, कॉन्फ़िगर की गई 0.01 की छूट के साथ; हेडर का कुल अंक संख्या के रूप में पढ़ा न जा सके तो यह `skipped` में बताता है कि वह चल नहीं सका। यह केवल जोड़ देखता है — अंकों का बँटवारा उचित है या नहीं, यह नहीं आँकता। |
| हमने अपनी प्रश्न-प्रकार सूची कभी नहीं बनाई। प्रश्न-प्रकार कॉलम पर उपकरण क्या करता है? | `PD-004` `skipped` में बताता है कि वह चल नहीं सका, क्योंकि उसकी `values` सूची खाली आती है: प्रश्न-प्रकारों के नाम आपकी संस्था की परिपाटी हैं और इंजन कोई सूची कठोरता से नहीं रखता। अपने मान कॉन्फ़िगर करने पर सूची से बाहर का `questionType` दर्ज होता है; तब यह नियम केवल सूची-सदस्यता देखता है और प्रश्न-प्रकार के अनुसार कोई संरचना-जाँच नहीं करता। |
| कठिनाई कॉलम में एक पंक्ति में `1.2` है और दूसरी में `中等` — क्या लौटता है? | `PD-005` उस मान को दर्ज करता है जिसे संख्या के रूप में नहीं पढ़ा जा सकता, और उसे भी जो कॉन्फ़िगर की गई `min`/`max` सीमा 0–1 से बाहर है। यह सीमा आपकी संस्था की परिपाटी है, एकमात्र पैमाना नहीं — 1–5 या प्रतिशत के लिए `min`/`max` बदलें या नियम बंद करें। यह केवल सीमा देखता है, कठिनाई उपयुक्त है या नहीं यह कभी नहीं, और यह `info` पर सीमित है। |
| दो प्रश्नों पर एक ही yotta पहचानकर्ता है। यह खाली पहचानकर्ता से बुरा क्यों है? | `PD-006` दोहराया गया मान दर्ज करता है, तुलना में खाली स्थान छोड़ देता है, क्योंकि यह विश्लेषण-परिणाम आयात करने पर मौजूद प्रश्न चुपचाप अधिलिखित हो जाएगा; खाली पहचानकर्ता केवल उस एक प्रश्न को बाहर रखता है। किसी पंक्ति में पहचानकर्ता न भरा हो तो नियम `skipped` में बताता है कि वह चल नहीं सका। यह उपस्थिति और अद्वितीयता देखता है, उससे आगे कुछ नहीं। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-paper-doc-adapter
dsh --profile <name> --dump-config | grep 'dsh-paper-doc-adapter'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/paper-doc-adapter.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-paper-doc-adapter
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-paper-doc-adapter contributors.
