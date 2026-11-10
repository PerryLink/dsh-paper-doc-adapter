#!/usr/bin/env python3
"""README visuals for dsh-paper-doc-adapter, derived from the shipped material.

Every figure below is built from this repository, not invented:

  * rules/paper-doc-adapter.yaml — version 2026.1, 8 rules PD-001…PD-008,
    7 distinct check kinds (presenceAny, sum, enum, number, unique, presence,
    containsAny), 2 institutional-configuration rules capped at info, and
    PD-004 shipping with `values: []` (so it reports itself in `skipped`).
  * src/model.ts — the column aliases (题号/questionNo, 题干/stem, …), the
    header fields (totalScore, durationMin, subject, …) and `parseMaterial`.
  * src/index.ts — `resolvePackageFile` + `loadRulesetFile`, the tool
    `paper_doc_adapter`, and the two-sided gate: a rule only runs when the
    material carries the column *and* the rule pack declares the check.
  * samples/quickstart/ — one parsed row (高二, 2026 版, totalScore 3,
    durationMin 90, difficulty 0.72, YOTTA-2026-0001), empty 题号 and 题干;
    real output: issueCount 1 (PD-001 warn), summary 0/1/0, skippedCount 1
    (PD-004, `values` unset).
  * src/shared/rows.ts — every handler calls `ctx.skip(reason)` when the
    column or the rule configuration is missing; nothing passes silently.

Two figures:

  hero 1440x576 (Pillow, 4 files: zh/en x light/dark)
      The left column is the plugin name and its promise. The right side is
      one real material row, dissected: six field tiles (the empty 题号 and
      题干 ringed in amber), a locator strip naming `row 1 · questionNo +
      stem`, the eight-rule pack rail, and the two output registers that the
      quickstart actually produces — one PD-001 difference and one skipped
      PD-004. It is a locator strip for a paper register, not a generic flow.

  flow 1100x660 (hand-written SVG, 2 files)
      A two-sided boundary gate. The left channel is the material
      (JSON/YAML → parseTable), the right channel is the rule pack
      (loadRulesetFile validation), and eight rules sit on a central spine
      that only lets a rule through when both sides hold. PD-004's right side
      is empty (`values: []`), so that row is dashed and falls into skipped.
      At the bottom the spine forks into the two output registers: issues
      (locator.row / column) and skipped (reason), then `buildView` emits
      markdown + reportJson.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow + Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import math
import os
from html import escape
from unicodedata import east_asian_width

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"
FONT_CJK_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
FONT_MONO_BOLD = r"C:\Windows\Fonts\consolab.ttf"
for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_MONO_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(f"FATAL: font missing: {_p}")

FONT_FILES = {"cjk": FONT_CJK, "cjk_bold": FONT_CJK_BOLD,
              "mono": FONT_MONO, "mono_bold": FONT_MONO_BOLD}

RADIUS = 22
SHADOW = 24

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", card_edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", accent_soft="#7a68c9",
        warn="#b45309", info="#4B67B4", green="#16a34a",
        pill="#ece7f9", band="#f5f2fb", grid="#e7e4f0",
        mark="#b45309", mark_bg="#fdf3e9", mark_edge="#e6d0ab",
        blue_bg="#eef2fb", blue_edge="#c6d0ea",
        green_bg="#eef8ef", green_edge="#c2dfc8",
        shadow=(32, 26, 64),
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", card_edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", accent_soft="#8496f5",
        warn="#d9a441", info="#8496f5", green="#3fb950",
        pill="#242d42", band="#202839", grid="#262f42",
        mark="#d9a441", mark_bg="#2a2216", mark_edge="#7a5a2a",
        blue_bg="#1f2638", blue_edge="#3d4a70",
        green_bg="#17251c", green_edge="#2f5a3a",
        shadow=(0, 0, 0),
    ),
}


# --------------------------------------------------------------------------
# Pillow helpers
# --------------------------------------------------------------------------
def font(size: int, kind: str = "cjk_bold") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], int(size))


def hx(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(base)
    a, b = hx(c1), hx(c2)
    for y in range(h):
        t = 0.15 * (y / h) + 0.85 * (y / h) ** 1.35
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: tuple,
         alpha: int = 40) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for i in range(9, 0, -1):
        rr = r * i / 9
        draw.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                     fill=color + (int(alpha * (1 - i / 10)),))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def card(img: Image.Image, box: tuple, s: dict, radius: int = RADIUS,
         shadow: int = SHADOW, fill: str | None = None) -> Image.Image:
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -3):
        sd.rounded_rectangle([x0 - i // 5, y0 + i // 2, x1 + i // 5, y1 + i],
                             radius=radius + i // 5,
                             fill=s["shadow"] + (int(9 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(10)))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                           outline=hx(s["card_edge"]), width=2)
    return base.convert("RGB")


_SCRATCH = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: int, kind: str) -> float:
    return _SCRATCH.textlength(text, font=font(size, kind))


def require_w(text: str, size: int, kind: str, max_w: float, what: str) -> None:
    width = measure(text, size, kind)
    if width > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs "
                         f"{width:.1f}px > {max_w}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    for size in range(start, minimum - 1, -1):
        if measure(text, size, kind) <= max_w:
            return size
    raise SystemExit(f"FATAL: text does not fit {max_w}px at >= {minimum}px: "
                     f"{text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


def pill(img: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 17, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold") -> tuple[int, int]:
    draw = ImageDraw.Draw(img)
    f = font(size, kind)
    width = draw.textlength(text, font=f)
    x, y = xy
    h = size + 20
    draw.rounded_rectangle([x, y, x + width + 30, y + h], radius=h // 2,
                           fill=hx(bg or s["pill"]))
    draw.text((x + 15, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
              anchor="lm")
    return int(x + width + 30), int(y + h)


def chip(img: Image.Image, xy: tuple[int, int], text: str, fg: str, bg: str,
         size: int = 11, kind: str = "cjk_bold", padx: int = 9,
         height: int = 20) -> int:
    draw = ImageDraw.Draw(img)
    f = font(size, kind)
    width = draw.textlength(text, font=f)
    x, y = xy
    draw.rounded_rectangle([x, y, x + width + padx * 2, y + height],
                           radius=height // 2, fill=hx(bg))
    draw.text((x + padx, y + height / 2), text, font=f, fill=hx(fg),
              anchor="lm")
    return int(width + padx * 2)


def _rrect_perimeter(box: tuple[int, int, int, int], r: int,
                     step: float = 2.0) -> list[tuple[float, float]]:
    """Sample a rounded-rectangle perimeter, clockwise from the top-left arc."""
    x0, y0, x1, y1 = box
    r = min(r, (x1 - x0) // 2, (y1 - y0) // 2)
    pts: list[tuple[float, float]] = []

    def arc(cx: float, cy: float, a0: float, a1: float) -> None:
        n = max(4, int(abs(a1 - a0) * r / step))
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    def edge(a: tuple[float, float], b: tuple[float, float]) -> None:
        dist = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(dist / step))
        for i in range(1, n + 1):
            t = i / n
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))

    arc(x0 + r, y0 + r, 180, 270)
    edge((x0 + r, y0), (x1 - r, y0))
    arc(x1 - r, y0 + r, 270, 360)
    edge((x1, y0 + r), (x1, y1 - r))
    arc(x1 - r, y1 - r, 0, 90)
    edge((x1 - r, y1), (x0 + r, y1))
    arc(x0 + r, y1 - r, 90, 180)
    edge((x0, y1 - r), (x0, y0 + r))
    return pts


def dashed_rrect(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
                 radius: int, color: str, width: int = 2, dash: int = 7,
                 gap: int = 5) -> None:
    pts = _rrect_perimeter(box, radius)
    on, remaining = True, float(dash)
    p0 = pts[0]
    for p1 in pts[1:]:
        seg = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        if seg == 0:
            continue
        consumed = 0.0
        while consumed < seg - 1e-6:
            take = min(remaining, seg - consumed)
            if on:
                t0, t1 = consumed / seg, (consumed + take) / seg
                draw.line([(p0[0] + (p1[0] - p0[0]) * t0,
                            p0[1] + (p1[1] - p0[1]) * t0),
                           (p0[0] + (p1[0] - p0[0]) * t1,
                            p0[1] + (p1[1] - p0[1]) * t1)],
                          fill=hx(color), width=width)
            consumed += take
            remaining -= take
            if remaining <= 1e-6:
                on = not on
                remaining = float(dash if on else gap)
        p0 = p1


HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 逐条核对",
        value=["把试卷解析结构逐条核到行与栏",
               "哪一行、哪一栏、差什么，一次说清"],
        sub=["8 条规则 · 7 类检查；空清单不等于没问题",
             "未执行的检查逐条写进 skipped，绝不静默通过"],
        meta="ruleset 2026.1 · PD-001…PD-008 · tool paper_doc_adapter",
        foot="Apache-2.0 · PerryLink DSH 插件家族 · 只读材料，不写原件",
        sheet_title="材料 · 1 行",
        chip_read="只读",
        chip_type="JSON | YAML",
        sheet_meta="高二 · 2026 版 · totalScore 3 · durationMin 90",
        tiles=[("题号", "questionNo", "空", "未填写", "blank"),
               ("题干", "stem", "空", "未填写", "blank"),
               ("答案", "answer", "B", "已填写", ""),
               ("分值", "score", "3", "本题分值", ""),
               ("难度", "difficulty", "0.72", "在 0–1 之内", ""),
               ("题目ID", "yottaId", "YOTTA-2026-0001", "唯一", "id")],
        locator="locator · row 1 · questionNo / stem",
        locator_right="issueCount 1",
        rules_label="规则包 · 8 条",
        rules_note="ruleset 2026.1 · 依据类型封顶级别",
        issue_title="第 1 行 · 题号 + 题干",
        found="questionNo、stem 都为空",
        expected="至少应填写一项",
        basis="依据 · 原则性条款推论，不伪造引文",
        skip_title="skipped 1",
        skip_tag="未执行",
        skip_rule="PD-004 · values 未配置",
        skip_note1="题型口径由本机构规定",
        skip_note2="本条不执行，也不静默通过",
        skip_note3="skipNotes 可附加备注",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · row-level check",
        value=["Check every parsed row and column",
               "row, column, and what is missing"],
        sub=["8 rules · 7 check kinds; an empty list is not a pass",
             "every check that cannot run says so in skipped"],
        meta="ruleset 2026.1 · PD-001…PD-008 · tool paper_doc_adapter",
        foot="Apache-2.0 · PerryLink DSH plugin family · reads one file, writes none",
        sheet_title="Material · 1 row",
        chip_read="read-only",
        chip_type="JSON | YAML",
        sheet_meta="Grade 11 · 2026 ed. · totalScore 3 · durationMin 90",
        tiles=[("Question no.", "questionNo", "empty", "not filled", "blank"),
               ("Stem", "stem", "empty", "not filled", "blank"),
               ("Answer", "answer", "B", "answered", ""),
               ("Score", "score", "3", "row score", ""),
               ("Difficulty", "difficulty", "0.72", "inside 0–1", ""),
               ("Question ID", "yottaId", "YOTTA-2026-0001", "unique", "id")],
        locator="locator · row 1 · questionNo / stem",
        locator_right="issueCount 1",
        rules_label="Rule pack · 8 rules",
        rules_note="ruleset 2026.1 · severity capped by basis",
        issue_title="Row 1 · questionNo + stem",
        found="questionNo and stem are both empty",
        expected="at least one must be filled",
        basis="basis · principle-derived, no fabricated quote",
        skip_title="skipped 1",
        skip_tag="not run",
        skip_rule="PD-004 · values not configured",
        skip_note1="question-type vocabulary is institutional",
        skip_note2="reported, never passed silently",
        skip_note3="skipNotes appends a note",
    ),
}


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    H = HERO[lang]
    W, HT = 1440, 576
    img = gradient(W, HT, s["bg_from"], s["bg_to"])
    img = glow(img, 1180, 26, 420, hx(s["accent"]),
               24 if skin == "light" else 38)
    img = glow(img, 72, 588, 300, hx(s["accent_soft"]),
               10 if skin == "light" else 16)

    draw = ImageDraw.Draw(img)
    m = 64
    col_w = 620

    # ---- left column: kicker / title / two value lines / sub / meta / foot --
    right_edge, _ = pill(img, (m, 50), H["kicker"], s, size=17)
    if right_edge > m + col_w:
        raise SystemExit(f"FATAL: kicker overflows: ends at {right_edge}")
    draw = ImageDraw.Draw(img)

    title_size = fit("dsh-paper-doc-adapter", "mono_bold", col_w, 54, 48)
    require_w("dsh-paper-doc-adapter", title_size, "mono_bold", col_w, "title")
    draw.text((m - 2, 104), "dsh-paper-doc-adapter",
              font=font(title_size, "mono_bold"), fill=hx(s["text"]))

    value_size = fit_lines(H["value"], "cjk_bold", col_w, 38, 30)
    for i, line in enumerate(H["value"]):
        require_w(line, value_size, "cjk_bold", col_w, "hero value")
        draw.text((m, 194 + i * 56), line,
                  font=font(value_size, "cjk_bold"), fill=hx(s["text"]))

    for i, line in enumerate(H["sub"]):
        require_w(line, 22, "cjk", col_w, "hero sub")
        draw.text((m + 1, 332 + i * 34), line, font=font(22, "cjk"),
                  fill=hx(s["sub"]))

    meta_size = fit(H["meta"], "cjk", col_w, 20, 12)
    require_w(H["meta"], meta_size, "cjk", col_w, "hero meta")
    require_w(H["foot"], 15, "cjk", col_w, "hero footer")
    draw.text((m + 1, 424), H["meta"], font=font(meta_size, "cjk"),
              fill=hx(s["faint"]))
    draw.line([m + 1, 462, m + col_w - 4, 462], fill=hx(s["grid"]), width=2)
    draw.text((m + 1, 480), H["foot"], font=font(15, "cjk"),
              fill=hx(s["faint"]))

    # ---- right top: one material row, six field tiles ----------------------
    img = card(img, (700, 36, 1376, 288), s, radius=RADIUS, shadow=SHADOW)
    draw = ImageDraw.Draw(img)
    draw.text((724, 52), H["sheet_title"], font=font(15, "cjk_bold"),
              fill=hx(s["text"]))
    require_w(H["sheet_title"], 15, "cjk_bold", 220, "sheet title")

    # chips are laid out from the right edge so their widths never overlap
    type_w = int(measure(H["chip_type"], 11, "cjk_bold")) + 18
    read_w = int(measure(H["chip_read"], 11, "cjk_bold")) + 18
    read_x = 1352 - read_w
    type_x = read_x - 8 - type_w
    chip(img, (type_x, 47), H["chip_type"], s["faint"], s["band"], size=11)
    chip(img, (read_x, 47), H["chip_read"], s["accent"], s["pill"], size=11)
    draw = ImageDraw.Draw(img)

    draw.text((724, 78), H["sheet_meta"], font=font(13, "cjk"),
              fill=hx(s["faint"]))
    require_w(H["sheet_meta"], 13, "cjk", 560, "sheet meta")

    widths = [92, 92, 84, 84, 92, 156]
    gap = 8
    tile_y, tile_h = 104, 104
    tile_x = 724
    for i, (label, field_name, value, status, kind) in enumerate(H["tiles"]):
        tw = widths[i]
        x = tile_x
        tile_x += tw + gap
        box = (x, tile_y, x + tw, tile_y + tile_h)
        marked = kind == "blank"
        if marked:
            draw.rounded_rectangle(box, radius=14, fill=hx(s["mark_bg"]))
            dashed_rrect(draw, box, 14, s["mark"], width=2, dash=7, gap=5)
        else:
            draw.rounded_rectangle(box, radius=14, fill=hx(s["band"]),
                                   outline=hx(s["card_edge"]), width=1)
        draw.text((x + 10, tile_y + 9), label, font=font(12, "cjk_bold"),
                  fill=hx(s["mark"] if marked else s["sub"]))
        draw.text((x + 10, tile_y + 26), field_name, font=font(11, "mono"),
                  fill=hx(s["faint"]))
        if kind == "blank":
            draw.text((x + 10, tile_y + 46), value, font=font(22, "cjk_bold"),
                      fill=hx(s["mark"]))
        elif kind == "id":
            draw.text((x + 10, tile_y + 48), value,
                      font=font(15, "mono_bold"), fill=hx(s["text"]))
        else:
            draw.text((x + 10, tile_y + 46), value,
                      font=font(20, "mono_bold"), fill=hx(s["text"]))
        draw.text((x + 10, tile_y + 80), status, font=font(11, "cjk"),
                  fill=hx(s["mark"] if marked else s["faint"]))

    # locator strip: names the row and the two columns, exactly as the report does
    loc = (724, 220, 1364, 264)
    draw.rounded_rectangle(loc, radius=12, fill=hx(s["blue_bg"]),
                           outline=hx(s["blue_edge"]), width=1)
    draw.ellipse([736, 235, 748, 247], outline=hx(s["accent"]), width=2)
    draw.line([742, 247, 742, 254], fill=hx(s["accent"]), width=2)
    draw.text((758, 242), H["locator"], font=font(13, "mono"),
              fill=hx(s["accent"]), anchor="lm")
    draw.text((1350, 242), H["locator_right"], font=font(12, "mono_bold"),
              fill=hx(s["accent"]), anchor="rm")
    require_w(H["locator"], 13, "mono", 500, "locator")
    require_w(H["locator_right"], 12, "mono_bold", 150, "locator count")

    # ---- rule rail: all eight rules, severity dot, PD-004 dashed -----------
    draw.text((700, 304), H["rules_label"], font=font(13, "cjk_bold"),
              fill=hx(s["text"]))
    draw.text((1376, 305), H["rules_note"], font=font(11, "cjk"),
              fill=hx(s["faint"]), anchor="ra")
    require_w(H["rules_label"], 13, "cjk_bold", 300, "rules label")
    require_w(H["rules_note"], 11, "cjk", 340, "rules note")

    chip_w, chip_gap = 75, 8
    sev = {"PD-004": "info", "PD-005": "info"}
    for i in range(8):
        rid = f"PD-{i + 1:03d}"
        x = 704 + i * (chip_w + chip_gap)
        box = (x, 322, x + chip_w, 356)
        skipped = rid == "PD-004"
        draw.rounded_rectangle(box, radius=17, fill=hx(s["card"]),
                               outline=hx(s["card_edge"]), width=1)
        if skipped:
            dashed_rrect(draw, box, 17, s["warn"], width=2, dash=6, gap=4)
        dot = s["accent"] if rid in sev else s["warn"]
        draw.ellipse([x + 12, 335, x + 20, 343], fill=hx(dot))
        draw.text((x + 26, 339), rid, font=font(13, "mono_bold"),
                  fill=hx(s["warn"] if skipped else s["text"]), anchor="lm")

    # ---- two output registers, both counts taken from samples/quickstart ---
    img = card(img, (700, 382, 1050, 536), s, radius=18, shadow=16)
    draw = ImageDraw.Draw(img)
    chip(img, (724, 398), "PD-001", s["warn"], s["mark_bg"], size=11)
    chip(img, (800, 398), "warn", s["warn"], s["mark_bg"], size=11)
    draw = ImageDraw.Draw(img)
    draw.text((724, 430), H["issue_title"], font=font(16, "cjk_bold"),
              fill=hx(s["text"]))
    require_w(H["issue_title"], 16, "cjk_bold", 310, "issue title")
    draw.text((724, 460), H["found"], font=font(13, "cjk"),
              fill=hx(s["warn"]))
    require_w(H["found"], 13, "cjk", 310, "issue found")
    draw.text((724, 486), H["expected"], font=font(12, "cjk"),
              fill=hx(s["sub"]))
    require_w(H["expected"], 12, "cjk", 310, "issue expected")
    draw.text((724, 510), H["basis"], font=font(11, "cjk"),
              fill=hx(s["faint"]))
    require_w(H["basis"], 11, "cjk", 310, "issue basis")

    img = card(img, (1070, 382, 1376, 536), s, radius=18, shadow=16)
    draw = ImageDraw.Draw(img)
    draw.text((1094, 394), H["skip_title"], font=font(17, "cjk_bold"),
              fill=hx(s["warn"]))
    draw.text((1352, 400), H["skip_tag"], font=font(11, "cjk"),
              fill=hx(s["warn"]), anchor="ra")
    draw.text((1094, 432), H["skip_rule"], font=font(13, "cjk_bold"),
              fill=hx(s["warn"]))
    require_w(H["skip_rule"], 13, "cjk_bold", 262, "skip rule")
    draw.text((1094, 458), H["skip_note1"], font=font(12, "cjk"),
              fill=hx(s["sub"]))
    require_w(H["skip_note1"], 12, "cjk", 262, "skip note 1")
    draw.text((1094, 482), H["skip_note2"], font=font(12, "cjk"),
              fill=hx(s["sub"]))
    require_w(H["skip_note2"], 12, "cjk", 262, "skip note 2")
    draw.text((1094, 508), H["skip_note3"], font=font(11, "cjk"),
              fill=hx(s["faint"]))
    require_w(H["skip_note3"], 11, "cjk", 262, "skip note 3")

    path = os.path.join(OUT, f"dsh-paper-doc-adapter-hero-{lang}-{skin}.webp")
    img.save(path, "WEBP", quality=90, method=6)
    print(f"wrote {os.path.relpath(path, ROOT)}")


# --------------------------------------------------------------------------
# flow SVG: two-sided boundary gate
# --------------------------------------------------------------------------
CJK = ("'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',"
       "'Source Han Sans SC',sans-serif")
MONO = "'Consolas','SFMono-Regular','Menlo',ui-monospace,monospace"

# (rule id, severity, check kind, rule-side configuration,
#  material columns (Chinese), material columns (field tokens), skipped)
FLOW_ROWS = [
    ("PD-001", "warn", "presenceAny", "fields: questionNo, stem",
     "题号 · 题干", "questionNo · stem", False),
    ("PD-002", "warn", "presenceAny", "fields: answer, explanation",
     "答案 · 解析", "answer · explanation", False),
    ("PD-003", "warn", "sum", "headerField: totalScore · tol 0.01",
     "分值 + 表头总分", "score + totalScore", False),
    ("PD-004", "info", "enum", "values: []",
     "题型", "questionType", True),
    ("PD-005", "info", "number", "min 0 · max 1",
     "难度", "difficulty", False),
    ("PD-006", "warn", "unique", "field: yottaId",
     "题目标识", "yottaId", False),
    ("PD-007", "warn", "presence", "field: knowledge",
     "知识点", "knowledge", False),
    ("PD-008", "warn", "containsAny", "terms: 11 项占位符",
     "题干", "stem", False),
]


def est_w(text: str, size: float, mono: bool = False) -> float:
    """Conservative text-width estimate for SVG layout assertions."""
    width = 0.0
    for ch in text:
        width += size * (1.0 if east_asian_width(ch) in "WF" else
                         (0.62 if mono else 0.56))
    return width


def flow_svg(skin: str) -> str:
    s = SKIN[skin]
    w, h = 1100, 660
    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="dsh-paper-doc-adapter two-sided boundary gate">')
    out.append("<defs>")
    out.append(
        f'<linearGradient id="bg" x1="0" y1="0" x2="0.35" y2="1">'
        f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
        f'<stop offset="1" stop-color="{s["bg_to"]}"/></linearGradient>')
    out.append(
        f'<filter id="soft" x="-30%" y="-30%" width="160%" height="170%">'
        f'<feDropShadow dx="0" dy="6" stdDeviation="8" '
        f'flood-color="#16122c" flood-opacity="'
        f'{0.10 if skin == "light" else 0.38}"/></filter>')
    out.append("</defs>")
    out.append(f'<rect width="{w}" height="{h}" fill="url(#bg)"/>')

    def text(x: float, y: float, value: str, size: float, fill: str,
             family: str = "cjk", weight: str | None = None,
             anchor: str | None = None, extra: str = "") -> None:
        attrs = [f'x="{x}"', f'y="{y}"', f'fill="{fill}"',
                 f'font-family="{CJK if family == "cjk" else MONO}"',
                 f'font-size="{size}"']
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if anchor:
            attrs.append(f'text-anchor="{anchor}"')
        if extra:
            attrs.append(extra)
        out.append(f'<text {" ".join(attrs)}>{escape(value)}</text>')

    def box(x0: float, y0: float, x1: float, y1: float, r: float,
            fill: str, stroke: str, sw: float = 1.5,
            dash: str | None = None, shadow: bool = False) -> None:
        attrs = [f'x="{x0}"', f'y="{y0}"', f'width="{x1 - x0}"',
                 f'height="{y1 - y0}"', f'rx="{r}"', f'fill="{fill}"',
                 f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if shadow:
            attrs.append('filter="url(#soft)"')
        out.append(f'<rect {" ".join(attrs)}/>')

    # header -----------------------------------------------------------------
    text(44, 57, "dsh-paper-doc-adapter", 28, s["text"], "mono", "700")
    text(44, 87,
         "材料列 × 规则配置：两侧都成立才核对；缺任一侧，该条自行进 skipped。",
         14.5, s["sub"])
    text(1056, 55, "tool paper_doc_adapter · ruleset 2026.1", 11.5,
         s["accent"], "mono", anchor="end")
    text(1056, 75, "rules/paper-doc-adapter.yaml · 8 rules · 7 kinds", 11,
         s["faint"], "mono", anchor="end")
    out.append(f'<line x1="44" y1="104" x2="1056" y2="104" '
               f'stroke="{s["grid"]}" stroke-width="1.5"/>')

    # channel headers --------------------------------------------------------
    text(48, 134, "材料侧 · material", 14, s["text"], weight="700")
    text(48, 157, "JSON | YAML → parseTable · 表头 + 每题一行", 11.5,
         s["sub"])
    text(1056, 134, "规则侧 · rules", 14, s["text"], weight="700",
         anchor="end")
    text(1056, 157, "loadRulesetFile 校验 → 8 条规则 · 依据类型封顶", 11.5,
         s["sub"], anchor="end")
    text(550, 134, "边界 · 两侧合取", 13.5, s["accent"], "cjk", "700",
         anchor="middle")
    text(550, 157, "任一侧缺 → skipped", 11, s["faint"], anchor="middle")

    # central spine ----------------------------------------------------------
    out.append(f'<line x1="550" y1="172" x2="550" y2="560" '
               f'stroke="{s["accent"]}" stroke-width="1.5" '
               f'stroke-dasharray="4 6" opacity="0.55"/>')

    # eight rule rows --------------------------------------------------------
    row_y = 188
    row_h, row_gap = 42, 4
    for rid, severity, kind, config, material_zh, material_field, skipped \
            in FLOW_ROWS:
        y = row_y
        row_y += row_h + row_gap
        left_box = (44, y, 496, y + row_h)
        right_box = (604, y, 1056, y + row_h)
        box(*left_box, 11, s["band"], s["grid"], 1.2)
        box(*right_box, 11, s["card"],
            s["warn"] if skipped else s["card_edge"], 1.8 if skipped else 1.2,
            "5 4" if skipped else None)
        text(58, y + 17, material_zh, 13.5, s["text"], weight="700")
        text(58, y + 33, material_field, 11, s["faint"], "mono")
        text(618, y + 17, kind, 13, s["text"], "mono", "700")
        text(618, y + 33, config, 11,
             s["warn"] if skipped else s["faint"], "mono")
        text(1044, y + 17, severity, 11,
             s["warn"] if severity == "warn" else s["info"],
             anchor="end")
        if skipped:
            text(1044, y + 33, "未配置", 11, s["warn"], anchor="end")

        # connectors into the gate
        out.append(f'<line x1="496" y1="{y + 21}" x2="504" y2="{y + 21}" '
                   f'stroke="{s["grid"]}" stroke-width="2"/>')
        right_dash = ' stroke-dasharray="4 3"' if skipped else ""
        out.append(
            f'<line x1="596" y1="{y + 21}" x2="604" y2="{y + 21}" '
            f'stroke="{s["warn"] if skipped else s["grid"]}" '
            f'stroke-width="2"{right_dash}/>')
        # gate badge on the spine
        box(504, y + 6, 596, y + 36, 15, s["card"],
            s["warn"] if skipped else s["accent"],
            2 if skipped else 1.5, "5 4" if skipped else None)
        text(550, y + 22, rid, 13,
             s["warn"] if skipped else s["text"], "mono", "700",
             anchor="middle")
        out.append(
            f'<circle cx="587" cy="{y + 12}" r="3.4" '
            f'fill="{s["info"] if severity == "info" else s["warn"]}"/>')

    # overflow assertions for the two columns
    for rid, severity, kind, config, material_zh, material_field, skipped \
            in FLOW_ROWS:
        if est_w(material_zh, 13.5) > 424:
            raise SystemExit(f"FATAL: flow material label too wide: {rid}")
        if est_w(material_field, 11, True) > 424:
            raise SystemExit(f"FATAL: flow field line too wide: {rid}")
        if est_w(kind, 13, True) > 330:
            raise SystemExit(f"FATAL: flow kind too wide: {rid}")
        if est_w(config, 11, True) > 360:
            raise SystemExit(f"FATAL: flow config too wide: {rid}")

    # fork into the two output registers (explicit arrowheads: marker
    # orientation on a short final segment is browser-dependent)
    out.append(f'<path d="M550 552 V564 H289 V566" fill="none" '
               f'stroke="{s["accent"]}" stroke-width="2"/>')
    out.append(f'<path d="M550 564 H811 V566" fill="none" '
               f'stroke="{s["accent"]}" stroke-width="2"/>')
    out.append(f'<path d="M289 573 L282 562 L296 562 Z" '
               f'fill="{s["accent"]}"/>')
    out.append(f'<path d="M811 573 L804 562 L818 562 Z" '
               f'fill="{s["accent"]}"/>')

    # output registers -------------------------------------------------------
    box(44, 574, 534, 630, 18, s["blue_bg"], s["blue_edge"], 1.5,
        shadow=True)
    box(566, 574, 1056, 630, 18, s["mark_bg"], s["mark_edge"], 1.5,
        shadow=True)
    text(60, 597, "issues · 差异清单", 14, s["text"], weight="700")
    text(60, 617, "locator.row · column · found / expected", 11,
         s["faint"], "mono")
    chip_box = (468, 586, 520, 608)
    box(*chip_box, 11, s["card"], s["blue_edge"], 1.2)
    text(494, 601, "1 条", 12, s["accent"], weight="700", anchor="middle")

    text(582, 597, "skipped · 未执行", 14, s["text"], weight="700")
    text(582, 617, "reason 逐条写明，绝不静默通过", 11, s["faint"])
    chip_box = (990, 586, 1042, 608)
    box(*chip_box, 11, s["card"], s["mark_edge"], 1.2)
    text(1016, 601, "1 条", 12, s["warn"], weight="700", anchor="middle")

    # footer ----------------------------------------------------------------
    text(44, 650, "只读材料 · 无网络 · 无模型调用 · 不改原件 · 不作定性结论",
         11, s["faint"])
    text(550, 650, "实线 · 两侧成立　虚线 · 缺侧进 skipped", 11,
         s["faint"], anchor="middle")
    text(1056, 650, "buildView → markdown + reportJson", 11,
         s["faint"], "mono", anchor="end")

    out.append("</svg>")
    return "\n".join(out) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            hero(lang, skin)
    for skin in ("light", "dark"):
        path = os.path.join(OUT,
                            f"dsh-paper-doc-adapter-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {os.path.relpath(path, ROOT)}")
    print("done: 4 hero WebP + 2 flow-v5 SVG")


if __name__ == "__main__":
    main()
