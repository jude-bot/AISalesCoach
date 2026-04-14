---
name: sred-doc-creator
description: >
  Create professional, on-brand SRED.ca PDF reports using reportlab. Use this skill whenever generating
  any PDF document for SRED.ca — coaching reports, manager summaries, baseline reports, quarterly reviews,
  proposals, client deliverables, or any branded PDF. Also triggers on: "create a report", "generate a PDF",
  "make a document", "build the report", "coaching report", "manager summary", "quarterly review",
  "branded PDF", or any request that involves producing a formatted PDF with SRED.ca branding. Even casual
  requests like "put that in a report" or "make it look nice" should activate this skill when SRED.ca
  context is present. If you are about to write reportlab code for an SRED.ca document and haven't loaded
  this skill yet, STOP and load it first.
---

# SRED.ca Doc Creator

This skill produces consistent, professional SRED.ca PDF reports using reportlab. It bundles a reusable
Python module (`scripts/sred_doc.py`) that every report generator should import. The module handles fonts,
colors, styles, tables, headers, page templates, and all the hard-won formatting rules that prevent
orphaned titles, overflowing text, and unreadable colors.

## Quick Start

Every SRED.ca PDF generator should start like this:

```python
import sys
sys.path.insert(0, "/path/to/sred-doc-creator/scripts")
from sred_doc import SREDDoc

doc = SREDDoc("My Report Title", "output.pdf")

# Add content using the builder methods
doc.cover_page("Report Title", "Subtitle or date", "Prepared for Someone")
doc.section_header("SECTION TITLE")
doc.body("Your paragraph text here.")
doc.sub_header("Sub-Section")
doc.body("More text under a sub-header.")
doc.branded_table(headers, rows)
doc.build()
```

The `SREDDoc` class registers fonts, sets up page templates (header bar + footer), and exposes
builder methods that automatically apply KeepTogether, Paragraph wrapping, and brand styles.

## The Module: `scripts/sred_doc.py`

Read the script before writing any report generator. It lives at:

```
sred-doc-creator/scripts/sred_doc.py
```

### What It Provides

**Colors** (use these constants, never raw hex in generators):
- `SRED_DARK_BLUE` (#2F2A4F) — headers, dark backgrounds, primary text on light backgrounds
- `SRED_GREEN` (#B7DB41) — backgrounds and accents ONLY. **Never use as text color** — it's nearly
  invisible on white. Use for table header backgrounds, accent bars, highlight fills.
- `SRED_LIGHT_BLUE` (#40BAEB) — links, secondary headers, chart accents
- `SRED_EMERALD` (#35B586) — readable green text on white. Use this when you want green text
  (positive indicators, success states, win callouts).
- `SRED_GRAY` (#4A4A4A) — body text
- `SRED_LIGHT_GRAY` (#E4E4E4) — borders, dividers, table row alternation

**Fonts** (auto-downloaded and registered):
- **Anton** — headings, section titles, cover page. Always uppercase.
- **Lato** (Regular, Bold, Italic, Light) — body text, table cells, captions. Sentence case.

**Pre-Built Styles** (via `doc.styles` dict):
- `Title` — Anton 28pt, SRED_DARK_BLUE
- `SectionHeader` — Anton 16pt, SRED_DARK_BLUE, uppercase, with top spacing
- `SubHeader` — Lato Bold 12pt, SRED_DARK_BLUE
- `BodyText` — Lato 10.5pt, SRED_GRAY, 14pt leading
- `SmallText` — Lato 8.5pt, SRED_GRAY
- `WinText` — Lato 10.5pt, SRED_EMERALD (for positive callouts)
- `CautionText` — Lato 10.5pt, warm amber (for warnings)
- `TableHeader` — Lato Bold 9.5pt, white text (for use on dark/green header rows)
- `TableCell` — Lato 9.5pt, SRED_GRAY, with wrapping

**Builder Methods:**
- `doc.cover_page(title, subtitle, prepared_for)` — branded cover with accent bar and logo placeholder
- `doc.section_header(text)` — Anton uppercase header, auto-wrapped with KeepTogether
- `doc.sub_header(text)` — Lato bold sub-header, auto-wrapped with next content via KeepTogether
- `doc.body(text)` — body paragraph
- `doc.body_keep(header_text, body_text)` — sub-header + body kept together (never orphans)
- `doc.win(text)` — emerald-colored positive callout
- `doc.caution(text)` — amber-colored watch item
- `doc.branded_table(headers, rows, col_widths=None)` — full-width table with brand styling,
  Paragraph-wrapped cells, alternating row colors. All cells auto-wrap — no overflow.
- `doc.kpi_row(metrics)` — horizontal KPI cards (label + value pairs)
- `doc.spacer(inches=0.2)` — vertical space
- `doc.page_break()` — force new page
- `doc.build()` — finalize and write PDF

**Page Template:**
- Letter size (8.5 × 11)
- 0.75" margins all sides
- Header: thin SRED_GREEN accent bar across top
- Footer: "SRED.ca" left-aligned, page number right-aligned, SRED_LIGHT_GRAY divider line
- Automatic page numbering

## Critical Rules (Burned Into the Module)

These rules exist because we learned them the hard way. The module enforces them automatically,
but you should understand them:

1. **#B7DB41 (lime green) is NEVER text color.** It's invisible on white backgrounds. The module
   uses it only for background fills and accent bars. When you want green text, use SRED_EMERALD
   (#35B586). This is enforced in the style definitions — there is no style that uses lime green
   as a text color.

2. **Every header stays with its content.** The module wraps all `section_header()` and `sub_header()`
   calls with KeepTogether so a title never appears alone at the bottom of a page. If you're building
   custom flowables outside the module, always use `KeepTogether([header, content])`.

3. **All table cells use Paragraph objects.** Plain strings in reportlab tables don't wrap — they
   overflow off the page. The `branded_table()` method automatically converts every cell to a
   `Paragraph` with the `TableCell` style. If you build tables manually, always wrap cell text in
   `Paragraph(text, table_cell_style)`.

4. **Escape ampersands in Paragraph text.** Reportlab's Paragraph uses XML parsing. Raw `&` will
   crash it. Always use `&amp;` in any text passed to Paragraph. The module's `_safe_text()` helper
   handles this automatically for builder methods.

5. **Anton is uppercase-only.** The module forces `.upper()` on all Anton-styled text. Don't fight it.

6. **Revenue privacy.** Evan's reports never include company-wide QuickBooks revenue. Only his
   personal deal metrics. This is a content rule, not a formatting rule — but it's critical enough
   to mention here.

## How to Use in a Report Generator

### Pattern 1: Simple Report

```python
from sred_doc import SREDDoc

doc = SREDDoc("Weekly Coaching Report", "coaching-report.pdf")
doc.cover_page("WEEKLY COACHING REPORT", "Week of April 7, 2026", "Prepared for Evan")

doc.section_header("THIS WEEK'S WINS")
doc.win("Think CNC technical discovery — masterclass in letting the client lead.")
doc.win("Two new pipeline deals added: Data & Scientific + D&R Electronics.")

doc.section_header("MEETING REVIEW")
doc.body_keep("Think CNC — April 6", "Logan led discovery while Evan supported...")

doc.section_header("PIPELINE HEALTH")
doc.branded_table(
    headers=["Stage", "Deals", "Notes"],
    rows=[
        ["Opportunity", "5", "TeckPath, Data & Sci, D&R Elec + MSR (stale)"],
        ["Assessment", "2", "Think CNC, Veda"],
        ["Follow-Up", "2", "Blueshift, FanLINC/Sparcks"],
    ],
    col_widths=[1.5, 0.8, 4.7]  # inches — must sum to ~7" (page width minus margins)
)

doc.section_header("COACHING FOCUS")
doc.body("This week: discovery question depth...")

doc.build()
```

### Pattern 2: KPI Dashboard Row

```python
doc.section_header("WEEK AT A GLANCE")
doc.kpi_row([
    ("Meetings", "4"),
    ("Pipeline Deals", "9"),
    ("Pipeline Value", "$135K"),
    ("Follow-Up Speed", "4.5 hrs"),
])
```

### Pattern 3: Custom Table with Specific Column Widths

```python
# Column widths in inches — always specify to prevent auto-sizing surprises
doc.branded_table(
    headers=["Metric", "This Week", "Last Week", "Trend"],
    rows=data_rows,
    col_widths=[2.5, 1.5, 1.5, 1.5]
)
```

### Pattern 4: Sections That Must Stay Together

```python
# For custom content that isn't just header + body:
from reportlab.platypus import KeepTogether
doc.story.append(KeepTogether([
    Paragraph("CUSTOM HEADER", doc.styles['SectionHeader']),
    Spacer(1, 6),
    some_table,
    Spacer(1, 6),
    Paragraph("Caption text", doc.styles['SmallText']),
]))
```

## Font Download Note

The module downloads Anton and Lato from GitHub on first use and caches them in a `_fonts/` directory
next to the script. This requires network access. The download uses a browser-like User-Agent header
because some CDNs block default Python requests.

If fonts are already cached, no network call is made.

## Checklist Before Generating Any SRED.ca PDF

Before writing or modifying any report generator, verify:

- [ ] Importing from `sred_doc.py` (not reinventing styles)
- [ ] Using `SRED_EMERALD` for any green text (never `SRED_GREEN`)
- [ ] All tables use `branded_table()` or manual Paragraph-wrapped cells
- [ ] All headers use `section_header()` / `sub_header()` (auto KeepTogether)
- [ ] Ampersands in text are escaped (`&amp;`) if building Paragraphs manually
- [ ] Column widths specified for all tables (sum to ~7 inches)
- [ ] No company revenue in Evan-facing reports
