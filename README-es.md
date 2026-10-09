# dsh-paper-doc-adapter — Verificación de la coherencia estructural de un examen analizado: tipo de pregunta, respuesta, puntuación e identificador yotta

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-paper-doc-adapter` lee un examen ya analizado —la cabecera del examen más una fila por pregunta— y comprueba la coherencia estructural interna de ese resultado: que cada pregunta registre su número y su enunciado, que haya una respuesta o una explicación, que la suma de las puntuaciones de las preguntas coincida con la puntuación total que indica la cabecera, que el tipo de pregunta provenga del vocabulario que usted configura, que el coeficiente de dificultad quede dentro de su rango, que los identificadores de pregunta estén presentes y no se repitan, que se registre un punto de conocimiento y que no quede ningún marcador de plantilla en el enunciado.

## Cómo se ve la salida

![Terminal demo of dsh-paper-doc-adapter: real output over its PD-006 fixture](https://raw.githubusercontent.com/PerryLink/dsh-paper-doc-adapter/main/docs/assets/dsh-paper-doc-adapter-demo.png)

Salida real de este plugin sobre su propio fixture de prueba `PD-006` — no es un montaje. El paquete de reglas no inventa citas, así que cada hallazgo nombra la cláusula aplicada y advierte que su texto no se obtuvo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| En una fila están vacíos tanto el número como el enunciado, ¿se informa de algo? | Sí. `PD-001` informa de la fila cuyo `questionNo` y `stem` están ambos vacíos, porque pide que se rellene al menos uno de los dos. Comprueba que algo esté puesto, no si la pregunta está bien redactada o el enunciado es riguroso. |
| Una pregunta tiene número y enunciado, pero ni respuesta ni explicación. | `PD-002` informa de esa fila: pide al menos uno de `answer` y `explanation`. No comprueba si la respuesta es correcta —eso es revisión de un experto de la materia, y el propio paquete lo dice. |
| Las puntuaciones suman 98 y la cabecera dice 100, ¿se detecta? | Sí. `PD-003` suma la columna `score` y compara el total con el `totalScore` que indica la cabecera del examen, con la tolerancia configurada de 0.01; si el total de la cabecera no es un número analizable, informa de que no pudo ejecutarse en `skipped`. Solo hace la suma: no juzga si el reparto de puntos es razonable. |
| Nunca declaramos nuestros propios tipos de pregunta. ¿Qué hace la herramienta con esa columna? | `PD-004` informa de que no pudo ejecutarse en `skipped`, porque su lista `values` viene vacía: nombrar los tipos de pregunta es convención de su institución y el motor no codifica ninguna lista. Al configurar sus valores, un `questionType` fuera de ellos se informa; la regla entonces solo comprueba la pertenencia y no hace ninguna validación estructural por tipo de pregunta. |
| La columna de dificultad trae `1.2` en una fila y `中等` en otra, ¿qué devuelve? | `PD-005` informa del valor que no puede analizar como número y del que queda fuera del rango `min`/`max` configurado, 0–1. Ese rango es convención de su institución, no la única escala: con 1–5 o porcentajes hay que cambiar `min`/`max` o desactivar la regla. Solo comprueba el rango, nunca si la dificultad es adecuada, y está limitada a `info`. |
| Dos preguntas llevan el mismo identificador yotta. ¿Por qué es peor que uno vacío? | `PD-006` informa del valor repetido, comparando sin espacios, porque importar ese resultado sobrescribiría en silencio una pregunta existente; un identificador vacío solo deja esa pregunta fuera. Si ninguna fila trae identificador, la regla informa de que no pudo ejecutarse en `skipped`. Comprueba presencia y unicidad, y nada más. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-paper-doc-adapter
dsh --profile <name> --dump-config | grep 'dsh-paper-doc-adapter'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/paper-doc-adapter.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-paper-doc-adapter
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-paper-doc-adapter contributors.
