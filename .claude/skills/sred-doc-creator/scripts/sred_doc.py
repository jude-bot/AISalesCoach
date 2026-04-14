"""
SRED.ca Document Creator — Reusable PDF generation module.

Import this module in any SRED.ca report generator to get consistent branding,
fonts, colors, styles, tables, and layout rules. Handles all the tricky bits:
font downloads, KeepTogether for headers, Paragraph-wrapped table cells,
readable color choices, and page templates with header/footer.

Usage:
    from sred_doc import SREDDoc

    doc = SREDDoc("Report Title", "output.pdf")
    doc.cover_page("TITLE", "Subtitle", "Prepared for Someone")
    doc.section_header("SECTION NAME")
    doc.body("Your text here.")
    doc.branded_table(["Col A", "Col B"], [["val1", "val2"]])
    doc.build()
"""

import os
import urllib.request
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor


# =============================================================================
# BRAND COLORS
# =============================================================================
# Usage rules:
#   SRED_GREEN  → backgrounds and accents ONLY. Never as text color.
#   SRED_EMERALD → readable green text on white backgrounds.
#   SRED_DARK_BLUE → primary headers, dark backgrounds.
#   SRED_LIGHT_BLUE → links, secondary accents, chart colors.

SRED_DARK_BLUE = HexColor("#2F2A4F")
SRED_GREEN = HexColor("#B7DB41")       # Accent/background only — NOT for text
SRED_LIGHT_BLUE = HexColor("#40BAEB")
SRED_EMERALD = HexColor("#35B586")     # Use this for readable green text
SRED_GRAY = HexColor("#4A4A4A")
SRED_LIGHT_GRAY = HexColor("#E4E4E4")
SRED_WARM_GRAY = HexColor("#B9B8A3")
SRED_NEAR_BLACK = HexColor("#202020")
SRED_WHITE = colors.white
SRED_AMBER = HexColor("#D4A017")       # Caution/watch items


# =============================================================================
# FONT MANAGEMENT
# =============================================================================

# Font files are cached in a _fonts/ directory next to this script.
_FONT_DIR = Path(__file__).parent / "_fonts"

_FONT_URLS = {
    "Anton-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",
    "Lato-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Regular.ttf",
    "Lato-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Bold.ttf",
    "Lato-Italic.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Italic.ttf",
    "Lato-Light.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-Light.ttf",
    "Lato-BoldItalic.ttf": "https://github.com/google/fonts/raw/main/ofl/lato/Lato-BoldItalic.ttf",
}

_FONT_REGISTERED = False


def _download_fonts():
    """Download Google Fonts to local cache if not already present."""
    _FONT_DIR.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

    for filename, url in _FONT_URLS.items():
        filepath = _FONT_DIR / filename
        if not filepath.exists():
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                filepath.write_bytes(response.read())


def _register_fonts():
    """Register Anton and Lato font families with reportlab."""
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return

    _download_fonts()

    font_map = {
        "Anton": "Anton-Regular.ttf",
        "Lato": "Lato-Regular.ttf",
        "Lato-Bold": "Lato-Bold.ttf",
        "Lato-Italic": "Lato-Italic.ttf",
        "Lato-Light": "Lato-Light.ttf",
        "Lato-BoldItalic": "Lato-BoldItalic.ttf",
    }

    for font_name, filename in font_map.items():
        filepath = str(_FONT_DIR / filename)
        try:
            pdfmetrics.registerFont(TTFont(font_name, filepath))
        except Exception:
            pass  # Font may already be registered

    _FONT_REGISTERED = True


# =============================================================================
# TEXT SAFETY
# =============================================================================

def _safe_text(text):
    """Escape characters that break reportlab's XML Paragraph parser.

    Handles: & → &amp;, < → &lt;, > → &gt;
    Preserves already-escaped entities and intentional XML tags like <b>, <i>, <br/>.
    """
    if not isinstance(text, str):
        text = str(text)

    # Replace bare ampersands (not already part of an entity)
    import re
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', text)

    return text


# =============================================================================
# SRED DOC CLASS
# =============================================================================

class SREDDoc:
    """Builder for SRED.ca branded PDF documents.

    Handles page setup, fonts, styles, and provides methods for adding
    content with automatic branding, KeepTogether, and Paragraph wrapping.
    """

    def __init__(self, title, output_path, page_size=letter, margins=None):
        """Initialize the document.

        Args:
            title: Document title (used in PDF metadata).
            output_path: File path for the generated PDF.
            page_size: Page dimensions (default: letter = 8.5 x 11).
            margins: Dict with keys top, bottom, left, right (in inches).
                     Defaults to 0.75" all around.
        """
        _register_fonts()

        if margins is None:
            margins = {"top": 0.75, "bottom": 0.75, "left": 0.75, "right": 0.75}

        self.title = title
        self.output_path = output_path
        self.page_width, self.page_height = page_size
        self.margins = margins

        # Usable content width (for table column calculations)
        self.content_width = self.page_width - (margins["left"] + margins["right"]) * inch

        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=page_size,
            topMargin=margins["top"] * inch,
            bottomMargin=margins["bottom"] * inch,
            leftMargin=margins["left"] * inch,
            rightMargin=margins["right"] * inch,
            title=title,
            author="SRED.ca",
        )

        self.story = []
        self.styles = self._build_styles()

        # Track whether we need KeepTogether binding for the next content
        self._pending_header = None

    def _build_styles(self):
        """Create the full set of SRED.ca branded paragraph styles."""
        styles = {}

        styles["Title"] = ParagraphStyle(
            "SREDTitle",
            fontName="Anton",
            fontSize=28,
            leading=34,
            textColor=SRED_DARK_BLUE,
            alignment=TA_LEFT,
            spaceAfter=6,
        )

        styles["Subtitle"] = ParagraphStyle(
            "SREDSubtitle",
            fontName="Lato",
            fontSize=14,
            leading=18,
            textColor=SRED_LIGHT_BLUE,
            alignment=TA_LEFT,
            spaceAfter=4,
        )

        styles["SectionHeader"] = ParagraphStyle(
            "SREDSectionHeader",
            fontName="Anton",
            fontSize=16,
            leading=20,
            textColor=SRED_DARK_BLUE,
            spaceBefore=18,
            spaceAfter=8,
            alignment=TA_LEFT,
        )

        styles["SubHeader"] = ParagraphStyle(
            "SREDSubHeader",
            fontName="Lato-Bold",
            fontSize=12,
            leading=15,
            textColor=SRED_DARK_BLUE,
            spaceBefore=10,
            spaceAfter=4,
            alignment=TA_LEFT,
        )

        styles["BodyText"] = ParagraphStyle(
            "SREDBodyText",
            fontName="Lato",
            fontSize=10.5,
            leading=14,
            textColor=SRED_GRAY,
            spaceAfter=8,
            alignment=TA_LEFT,
        )

        styles["SmallText"] = ParagraphStyle(
            "SREDSmallText",
            fontName="Lato",
            fontSize=8.5,
            leading=11,
            textColor=SRED_GRAY,
            spaceAfter=4,
        )

        styles["WinText"] = ParagraphStyle(
            "SREDWinText",
            fontName="Lato",
            fontSize=10.5,
            leading=14,
            textColor=SRED_GRAY,
            spaceAfter=6,
            leftIndent=12,
            bulletIndent=0,
        )

        styles["CautionText"] = ParagraphStyle(
            "SREDCautionText",
            fontName="Lato",
            fontSize=10.5,
            leading=14,
            textColor=SRED_GRAY,
            spaceAfter=6,
            leftIndent=12,
            bulletIndent=0,
        )

        styles["TableHeader"] = ParagraphStyle(
            "SREDTableHeader",
            fontName="Lato-Bold",
            fontSize=9.5,
            leading=12,
            textColor=SRED_WHITE,
            alignment=TA_LEFT,
        )

        styles["TableCell"] = ParagraphStyle(
            "SREDTableCell",
            fontName="Lato",
            fontSize=9.5,
            leading=12,
            textColor=SRED_GRAY,
            alignment=TA_LEFT,
        )

        styles["TableCellBold"] = ParagraphStyle(
            "SREDTableCellBold",
            fontName="Lato-Bold",
            fontSize=9.5,
            leading=12,
            textColor=SRED_DARK_BLUE,
            alignment=TA_LEFT,
        )

        styles["TableCellEmerald"] = ParagraphStyle(
            "SREDTableCellEmerald",
            fontName="Lato",
            fontSize=9.5,
            leading=12,
            textColor=SRED_GRAY,
            alignment=TA_LEFT,
        )

        styles["TableCellAmber"] = ParagraphStyle(
            "SREDTableCellAmber",
            fontName="Lato",
            fontSize=9.5,
            leading=12,
            textColor=SRED_GRAY,
            alignment=TA_LEFT,
        )

        styles["KPIValue"] = ParagraphStyle(
            "SREDKPIValue",
            fontName="Anton",
            fontSize=22,
            leading=26,
            textColor=SRED_DARK_BLUE,
            alignment=TA_CENTER,
        )

        styles["KPILabel"] = ParagraphStyle(
            "SREDKPILabel",
            fontName="Lato",
            fontSize=9,
            leading=11,
            textColor=SRED_GRAY,
            alignment=TA_CENTER,
        )

        styles["FooterText"] = ParagraphStyle(
            "SREDFooterText",
            fontName="Lato",
            fontSize=8,
            leading=10,
            textColor=SRED_WARM_GRAY,
        )

        styles["CoverPrepared"] = ParagraphStyle(
            "SREDCoverPrepared",
            fontName="Lato-Light",
            fontSize=11,
            leading=14,
            textColor=SRED_GRAY,
            spaceAfter=4,
        )

        return styles

    # =========================================================================
    # PAGE TEMPLATE (header bar + footer)
    # =========================================================================

    def _header_footer(self, canvas, doc):
        """Draw the page header accent bar and footer on every page."""
        canvas.saveState()

        # Header: thin green accent bar across top
        bar_height = 4
        canvas.setFillColor(SRED_GREEN)
        canvas.rect(0, self.page_height - bar_height, self.page_width, bar_height, fill=1, stroke=0)

        # Footer: divider line + "SRED.ca" left + page number right
        footer_y = self.margins["bottom"] * inch - 20
        margin_left = self.margins["left"] * inch
        margin_right = self.page_width - self.margins["right"] * inch

        # Divider line
        canvas.setStrokeColor(SRED_LIGHT_GRAY)
        canvas.setLineWidth(0.5)
        canvas.line(margin_left, footer_y + 12, margin_right, footer_y + 12)

        # "SRED.ca" left
        canvas.setFont("Lato", 8)
        canvas.setFillColor(SRED_WARM_GRAY)
        canvas.drawString(margin_left, footer_y, "SRED.ca")

        # Page number right
        canvas.drawRightString(margin_right, footer_y, f"Page {doc.page}")

        canvas.restoreState()

    def _first_page_template(self, canvas, doc):
        """First page can optionally skip header/footer (e.g., for cover pages)."""
        # For now, same as other pages. Override if cover pages need blank chrome.
        self._header_footer(canvas, doc)

    # =========================================================================
    # CONTENT BUILDER METHODS
    # =========================================================================

    def cover_page(self, title, subtitle="", prepared_for=""):
        """Add a branded cover page.

        Args:
            title: Main title (will be uppercased, Anton font).
            subtitle: Secondary line (date, period, etc.).
            prepared_for: "Prepared for [Name]" line.
        """
        self.story.append(Spacer(1, 2 * inch))

        # Accent bar
        accent = HRFlowable(
            width="30%", thickness=4, color=SRED_GREEN,
            spaceBefore=0, spaceAfter=20, hAlign="LEFT"
        )
        self.story.append(accent)

        # Title
        self.story.append(Paragraph(_safe_text(title.upper()), self.styles["Title"]))

        # Subtitle
        if subtitle:
            self.story.append(Paragraph(_safe_text(subtitle), self.styles["Subtitle"]))

        # Prepared for
        if prepared_for:
            self.story.append(Spacer(1, 12))
            self.story.append(Paragraph(
                _safe_text(f"Prepared for {prepared_for}"),
                self.styles["CoverPrepared"]
            ))

        # "SRED.ca" branding at bottom of cover
        self.story.append(Spacer(1, 3 * inch))
        self.story.append(Paragraph("SRED.CA", ParagraphStyle(
            "CoverBrand", fontName="Anton", fontSize=14,
            textColor=SRED_LIGHT_BLUE, alignment=TA_LEFT
        )))

        self.story.append(PageBreak())

    def section_header(self, text):
        """Add a section header (Anton, uppercase).

        Automatically kept together with the next content added via body(),
        sub_header(), branded_table(), win(), or caution().
        """
        self._flush_pending_header()
        self._pending_header = Paragraph(_safe_text(text.upper()), self.styles["SectionHeader"])

    def sub_header(self, text):
        """Add a sub-header (Lato Bold).

        Automatically kept together with the next content added.
        """
        self._flush_pending_header()
        self._pending_header = Paragraph(_safe_text(text), self.styles["SubHeader"])

    def body(self, text):
        """Add a body text paragraph."""
        para = Paragraph(_safe_text(text), self.styles["BodyText"])
        self._append_with_header(para)

    def body_keep(self, header_text, body_text):
        """Add a sub-header + body paragraph, kept together on the same page.

        This is the most common pattern for preventing orphaned titles.
        """
        self._flush_pending_header()
        header = Paragraph(_safe_text(header_text), self.styles["SubHeader"])
        body = Paragraph(_safe_text(body_text), self.styles["BodyText"])
        self.story.append(KeepTogether([header, body]))

    def small(self, text):
        """Add small text (captions, footnotes)."""
        para = Paragraph(_safe_text(text), self.styles["SmallText"])
        self._append_with_header(para)

    def win(self, text):
        """Add a positive callout in emerald green."""
        bullet = f"\u2713 {text}"
        para = Paragraph(_safe_text(bullet), self.styles["WinText"])
        self._append_with_header(para)

    def caution(self, text):
        """Add a watch/caution item in amber."""
        bullet = f"\u26A0 {text}"
        para = Paragraph(_safe_text(bullet), self.styles["CautionText"])
        self._append_with_header(para)

    def wins(self, items):
        """Add a list of win items, keeping the first 2 with the preceding header."""
        paras = [Paragraph(_safe_text(f"\u2713 {item}"), self.styles["WinText"]) for item in items]
        if self._pending_header and len(paras) >= 1:
            keep = [self._pending_header] + paras[:2]
            self.story.append(KeepTogether(keep))
            self._pending_header = None
            for p in paras[2:]:
                self.story.append(p)
        else:
            self._flush_pending_header()
            for p in paras:
                self.story.append(p)

    def cautions(self, items):
        """Add a list of caution items, keeping the first 2 with the preceding header."""
        paras = [Paragraph(_safe_text(f"\u26A0 {item}"), self.styles["CautionText"]) for item in items]
        if self._pending_header and len(paras) >= 1:
            keep = [self._pending_header] + paras[:2]
            self.story.append(KeepTogether(keep))
            self._pending_header = None
            for p in paras[2:]:
                self.story.append(p)
        else:
            self._flush_pending_header()
            for p in paras:
                self.story.append(p)

    def branded_table(self, headers, rows, col_widths=None, header_bg=None):
        """Add a professionally styled table with auto-wrapping cells.

        Args:
            headers: List of column header strings.
            rows: List of lists — each inner list is a row of cell values.
                  Cell values can be strings (auto-wrapped) or Paragraph objects.
            col_widths: List of column widths in inches. Should sum to ~7"
                        (content width). If None, columns split evenly.
            header_bg: Background color for header row. Default: SRED_DARK_BLUE.
        """
        if header_bg is None:
            header_bg = SRED_DARK_BLUE

        # Convert widths from inches to points
        if col_widths:
            col_widths_pts = [w * inch for w in col_widths]
        else:
            col_widths_pts = [self.content_width / len(headers)] * len(headers)

        # Build header row with Paragraph objects
        header_row = [
            Paragraph(_safe_text(h), self.styles["TableHeader"]) for h in headers
        ]

        # Build data rows — convert plain strings to Paragraphs for wrapping
        data_rows = []
        for row in rows:
            processed_row = []
            for cell in row:
                if isinstance(cell, Paragraph):
                    processed_row.append(cell)
                elif isinstance(cell, str):
                    processed_row.append(
                        Paragraph(_safe_text(cell), self.styles["TableCell"])
                    )
                else:
                    processed_row.append(
                        Paragraph(_safe_text(str(cell)), self.styles["TableCell"])
                    )
            data_rows.append(processed_row)

        table_data = [header_row] + data_rows

        table = Table(table_data, colWidths=col_widths_pts, repeatRows=1)

        # Build style commands
        style_commands = [
            # Header row
            ("BACKGROUND", (0, 0), (-1, 0), header_bg),
            ("TEXTCOLOR", (0, 0), (-1, 0), SRED_WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Lato-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9.5),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),

            # Data rows
            ("FONTNAME", (0, 1), (-1, -1), "Lato"),
            ("FONTSIZE", (0, 1), (-1, -1), 9.5),
            ("TEXTCOLOR", (0, 1), (-1, -1), SRED_GRAY),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),

            # Grid
            ("LINEBELOW", (0, 0), (-1, 0), 1, SRED_DARK_BLUE),
            ("LINEBELOW", (0, 1), (-1, -2), 0.5, SRED_LIGHT_GRAY),
            ("LINEBELOW", (0, -1), (-1, -1), 1, SRED_LIGHT_GRAY),
        ]

        # Alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                style_commands.append(
                    ("BACKGROUND", (0, i), (-1, i), HexColor("#F8F8F8"))
                )

        table.setStyle(TableStyle(style_commands))

        self._append_with_header(table)

    def kpi_row(self, metrics, bg_color=None):
        """Add a horizontal row of KPI cards.

        Args:
            metrics: List of (label, value) tuples.
                     e.g., [("Meetings", "4"), ("Pipeline", "$135K")]
            bg_color: Background for the KPI card cells. Default: light gray.
        """
        if bg_color is None:
            bg_color = HexColor("#F5F5F5")

        col_count = len(metrics)
        col_width = self.content_width / col_count

        # Build cells: value on top, label below
        cells = []
        for label, value in metrics:
            cell_content = [
                Paragraph(_safe_text(str(value).upper()), self.styles["KPIValue"]),
                Paragraph(_safe_text(label), self.styles["KPILabel"]),
            ]
            cells.append(cell_content)

        # Create a table with one row, each cell containing a mini-table
        kpi_tables = []
        for cell_content in cells:
            mini = Table([[cell_content[0]], [cell_content[1]]],
                         colWidths=[col_width - 12])
            mini.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, -1), bg_color),
                ("ROUNDEDCORNERS", [4, 4, 4, 4]),
            ]))
            kpi_tables.append(mini)

        # Wrap in outer table for horizontal layout
        outer = Table([kpi_tables], colWidths=[col_width] * col_count)
        outer.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))

        self._append_with_header(outer)

    def accent_bar(self, width_pct="100%", thickness=3, color=None):
        """Add a horizontal accent bar (decorative divider)."""
        if color is None:
            color = SRED_GREEN
        self.story.append(HRFlowable(
            width=width_pct, thickness=thickness, color=color,
            spaceBefore=8, spaceAfter=8, hAlign="LEFT"
        ))

    def divider(self):
        """Add a subtle gray divider line."""
        self.story.append(HRFlowable(
            width="100%", thickness=0.5, color=SRED_LIGHT_GRAY,
            spaceBefore=12, spaceAfter=12, hAlign="LEFT"
        ))

    def spacer(self, inches_val=0.2):
        """Add vertical whitespace."""
        self.story.append(Spacer(1, inches_val * inch))

    def page_break(self):
        """Force a new page."""
        self._flush_pending_header()
        self.story.append(PageBreak())

    def raw(self, flowable):
        """Add any reportlab flowable directly to the story.

        Use this for custom content not covered by the builder methods.
        The flowable will be kept together with any pending header.
        """
        self._append_with_header(flowable)

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    def _flush_pending_header(self):
        """If there's an unattached header, flush it to the story standalone."""
        if self._pending_header is not None:
            self.story.append(self._pending_header)
            self._pending_header = None

    def _append_with_header(self, flowable):
        """Append content, wrapping it with any pending header in KeepTogether."""
        if self._pending_header is not None:
            self.story.append(KeepTogether([self._pending_header, flowable]))
            self._pending_header = None
        else:
            self.story.append(flowable)

    # =========================================================================
    # BUILD
    # =========================================================================

    def build(self):
        """Finalize and write the PDF file.

        Returns:
            The output file path.
        """
        self._flush_pending_header()

        self.doc.build(
            self.story,
            onFirstPage=self._header_footer,
            onLaterPages=self._header_footer,
        )

        return self.output_path


# =============================================================================
# CONVENIENCE — standalone usage for quick one-off documents
# =============================================================================

def quick_report(title, output_path, sections):
    """Generate a simple branded report from a dict of sections.

    Args:
        title: Report title for cover page.
        output_path: PDF file path.
        sections: OrderedDict or list of (header, content) tuples.
                  Content can be a string or list of strings.

    Returns:
        The output file path.
    """
    doc = SREDDoc(title, output_path)
    doc.cover_page(title, "", "")

    if isinstance(sections, dict):
        sections = sections.items()

    for header, content in sections:
        doc.section_header(header)
        if isinstance(content, list):
            for item in content:
                doc.body(item)
        else:
            doc.body(content)

    return doc.build()


def add_cover_page(story, title, subtitle="", prepared_for=""):
    """Add the standard SRED.ca cover page to any story list.

    Use this in generators that build their own SimpleDocTemplate
    instead of using SREDDoc. Produces the exact same cover page
    as SREDDoc.cover_page().

    Args:
        story: The list of flowables to append to.
        title: Main title (will be uppercased, Anton font).
        subtitle: Secondary line (date, period, etc.).
        prepared_for: "Prepared for [Name]" line.
    """
    _register_fonts()

    story.append(Spacer(1, 2 * inch))

    # Accent bar
    story.append(HRFlowable(
        width="30%", thickness=4, color=SRED_GREEN,
        spaceBefore=0, spaceAfter=20, hAlign="LEFT"
    ))

    # Title — Anton, uppercase, dark blue
    story.append(Paragraph(
        _safe_text(title.upper()),
        ParagraphStyle("CoverTitle", fontName="Anton", fontSize=28,
                       leading=34, textColor=SRED_DARK_BLUE, spaceAfter=6)
    ))

    # Subtitle — Lato, light blue
    if subtitle:
        story.append(Paragraph(
            _safe_text(subtitle),
            ParagraphStyle("CoverSub", fontName="Lato", fontSize=14,
                           leading=18, textColor=SRED_LIGHT_BLUE, spaceAfter=4)
        ))

    # Prepared for — Lato Light, gray
    if prepared_for:
        story.append(Spacer(1, 12))
        story.append(Paragraph(
            _safe_text(f"Prepared for {prepared_for}"),
            ParagraphStyle("CoverPrep", fontName="Lato-Light", fontSize=11,
                           leading=14, textColor=SRED_GRAY, spaceAfter=4)
        ))

    # SRED.CA branding at bottom
    story.append(Spacer(1, 3 * inch))
    story.append(Paragraph("SRED.CA", ParagraphStyle(
        "CoverBrand", fontName="Anton", fontSize=14,
        textColor=SRED_LIGHT_BLUE
    )))

    story.append(PageBreak())


def add_header_footer(canvas_obj, doc, page_width=letter[0], page_height=letter[1], margins=None):
    """Draw the standard SRED.ca header bar and footer on a page.

    Use as onFirstPage/onLaterPages callback in generators that build
    their own SimpleDocTemplate.

    Usage:
        doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    """
    if margins is None:
        margins = {"left": 0.75, "right": 0.75, "bottom": 0.75}

    canvas_obj.saveState()

    # Header: thin green accent bar
    canvas_obj.setFillColor(SRED_GREEN)
    canvas_obj.rect(0, page_height - 4, page_width, 4, fill=1, stroke=0)

    # Footer
    footer_y = margins["bottom"] * inch - 20
    margin_left = margins["left"] * inch
    margin_right = page_width - margins["right"] * inch

    # Divider line
    canvas_obj.setStrokeColor(SRED_LIGHT_GRAY)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(margin_left, footer_y + 12, margin_right, footer_y + 12)

    # "SRED.ca" left
    canvas_obj.setFont("Lato", 8)
    canvas_obj.setFillColor(SRED_WARM_GRAY)
    canvas_obj.drawString(margin_left, footer_y, "SRED.ca")

    # Page number right
    canvas_obj.drawRightString(margin_right, footer_y, f"Page {doc.page}")

    canvas_obj.restoreState()
