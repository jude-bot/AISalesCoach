#!/usr/bin/env python3
"""
SRED.ca Sales Coaching - Quarterly Review Report Generator

This script generates a quarterly review PDF report for SRED.ca's sales coaching program.
It pulls data from the sales coaching outputs and generates a 6-8 page PDF with:
- Cover page
- Quarter at a glance (KPI dashboard)
- Revenue trends (chart)
- Pipeline health (funnel visualization)
- Coaching progress (SDT tracking)
- Commitments review & next quarter preview

Configuration variables are clearly labeled at the top for easy quarterly updates.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add path to sred_doc module
sys.path.insert(0, "/sessions/ecstatic-eloquent-hamilton/mnt/sales-coach/.claude/skills/sred-doc-creator/scripts")

# Try to import required packages, with helpful install messages
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
    from reportlab.pdfgen import canvas
except ImportError:
    print("ERROR: reportlab not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "reportlab"])
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether
    from reportlab.pdfgen import canvas

# Import SRED.ca shared assets
from sred_doc import (
    SRED_DARK_BLUE, SRED_GREEN, SRED_LIGHT_BLUE, SRED_EMERALD,
    SRED_GRAY, SRED_LIGHT_GRAY, SRED_WARM_GRAY, SRED_AMBER, SRED_WHITE,
    _register_fonts, _safe_text, add_cover_page, add_header_footer
)

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError:
    print("ERROR: matplotlib not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--break-system-packages", "matplotlib"])
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

# ============================================================================
# CONFIGURATION VARIABLES - Update these for each quarter
# ============================================================================

QUARTER_NAME = "FY2026 Q4"
QUARTER_START_DATE = "February 1, 2026"
QUARTER_END_DATE = "April 30, 2026"
SALES_ASSOCIATE = "Evan Batchelor"
TITLE = "SRED.ca Sales Coaching - Quarterly Review"

# Personal Goals (Evan + Coach ONLY — not in manager summary)
# These are populated from evan-personal-goals.md each quarter.
# Set INCLUDE_PERSONAL_GOALS = False when generating the manager version.
INCLUDE_PERSONAL_GOALS = True

PERSONAL_GOALS = [
    {
        "title": "[To be set in first quarterly session]",
        "specific": "—",
        "measurable": "—",
        "achievable": "—",
        "relevant": "—",
        "timebound": "—",
        "status": "Not Started",       # Not Started / In Progress / On Track / At Risk / Complete
        "progress_pct": 0,
        "coach_notes": "First coaching cycle — goals will be set during the initial quarterly review session.",
    },
]

# Revenue & Deal Data
QUARTER_REVENUE = 25000  # Evan's Q4 deals: Sky High ERP ($10K) + Beacn 2026 ($15K)
DEALS_CLOSED_THIS_QUARTER = 2
DEALS_CLOSED_NAMES = ["Sky High ERP", "Beacn 2026"]  # Deal names
DEAL_VALUES = [10000, 15000]  # Corresponding values
ACTIVE_PIPELINE_VALUE = 135000
ACTIVE_PIPELINE_COUNT = 9
NEW_OPPORTUNITIES_COUNT = 7
MEETINGS_HELD_COUNT = 23  # From Fireflies data
PIPELINE_TOUCHES_PER_WEEK = 6.2  # avg active deals touched per week
POST_MEETING_FOLLOWUP_HOURS = 4.5  # avg hours between meeting end and follow-up email

# LinkedIn Outreach (Evan's HeyReach data)
LINKEDIN_CONNECTIONS_SENT = 287  # This quarter
LINKEDIN_CONNECTIONS_ACCEPTED = 50  # This quarter
LINKEDIN_ACCEPTANCE_RATE = 17.4  # percent
LINKEDIN_MESSAGES_SENT = 58  # This quarter
LINKEDIN_MESSAGES_REPLY_RATE = 25.7  # percent
LINKEDIN_INMAILS_SENT = 120  # This quarter
LINKEDIN_INMAIL_REPLY_RATE = 5.8  # percent

# Email Marketing (Prospecting Agent — bloom@connect + bloom@team)
PROSPECTING_EMAILS_SENT = 3200  # This quarter (automated sequences)
PROSPECTING_REPLIES_RECEIVED = 87  # Replies from prospects
PROSPECTING_REPLY_RATE = 2.7  # percent
PROSPECTING_MEETINGS_BOOKED = 4  # Meetings booked from outbound
EVAN_PERSONAL_EMAILS_SENT = 85  # Evan's personal emails this quarter
EVAN_PERSONAL_REPLY_RATE = 22.4  # percent

# YTD Progress
YTD_NEW_BUSINESS_ACTUAL = 160000
YTD_NEW_BUSINESS_TARGET = 240000
YTD_DEALS_ACTUAL = 9
YTD_DEALS_TARGET = 16
QUARTERLY_TARGET = 60000  # $240K / 4 quarters
QUARTERLY_ACTUAL = QUARTER_REVENUE

# Monthly Breakdown
MONTHLY_DATA = [
    {"month": "Feb 2026", "revenue": 0, "deals": 0, "pipeline_change": 2},
    {"month": "Mar 2026", "revenue": 10000, "deals": 1, "pipeline_change": 1},
    {"month": "Apr 2026 (7 days)", "revenue": 15000, "deals": 1, "pipeline_change": 3},
]

# Pipeline Stage Data
PIPELINE_STAGES = [
    {"stage": "Opportunity", "count": 5, "value": 70000},
    {"stage": "Assessment", "count": 1, "value": 15000},
    {"stage": "Tech Discovery", "count": 1, "value": 15000},
    {"stage": "Follow-Up", "count": 1, "value": 15000},
    {"stage": "Custom", "count": 1, "value": 15000},
]

# Coaching Sessions
COACHING_SESSIONS_THIS_QUARTER = 12

# SDT Progress (placeholders for this template run)
SDT_BASELINE = {"autonomy": "Developing", "competence": "Strong Foundation", "relatedness": "Natural Strength"}
SDT_CURRENT = {"autonomy": "Developing→Independent", "competence": "Strong", "relatedness": "Strong"}

# Behavioral Metrics
BEHAVIORAL_METRICS = [
    {"metric": "Talk Ratio", "baseline": "4-6%", "current": "6-8%", "change": "↑"},
    {"metric": "Pipeline Touches/Week", "baseline": "—", "current": "6.2", "change": "New"},
    {"metric": "Post-Meeting Follow-Up", "baseline": "—", "current": "4.5 hrs", "change": "New"},
    {"metric": "Win Rate", "baseline": "15.3%", "current": "18.5%", "change": "↑"},
    {"metric": "Avg Days to Close", "baseline": "94", "current": "87", "change": "↓"},
]

# Brand Colors — SRED.ca official palette
# Imported from sred_doc module:
# SRED_DARK_BLUE, SRED_GREEN, SRED_LIGHT_BLUE, SRED_EMERALD,
# SRED_GRAY, SRED_LIGHT_GRAY, SRED_WARM_GRAY, SRED_AMBER, SRED_WHITE
SRED_ORANGE = HexColor("#dd6b20")     # Warning accent
SRED_RED = HexColor("#e53e3e")        # Alert

# Output Path
OUTPUT_PATH = Path("/sessions/ecstatic-eloquent-hamilton/mnt/sales-coach/outputs")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
PDF_FILENAME = OUTPUT_PATH / "quarterly-review-FY2026-Q4-draft.pdf"

# ============================================================================
# FONT REGISTRATION — SRED.ca uses Anton (headings) and Lato (body)
# ============================================================================
# Font registration handled by _register_fonts() from sred_doc module
_register_fonts()

HEADING_FONT = 'Anton'
BODY_FONT = 'Lato'

# ============================================================================
# STYLE DEFINITIONS
# ============================================================================

styles = getSampleStyleSheet()

# Title style — Anton, UPPERCASE
title_style = ParagraphStyle(
    "CustomTitle",
    parent=styles["Heading1"],
    fontSize=28,
    textColor=SRED_DARK_BLUE,
    spaceAfter=12,
    fontName=HEADING_FONT,
)

# Section heading style — Anton, UPPERCASE
heading_style = ParagraphStyle(
    "CustomHeading",
    parent=styles["Heading2"],
    fontSize=16,
    textColor=SRED_DARK_BLUE,
    spaceAfter=10,
    fontName=HEADING_FONT,
)

# Normal body text — Lato
body_style = ParagraphStyle(
    "CustomBody",
    parent=styles["BodyText"],
    fontSize=10,
    fontName=BODY_FONT,
    leading=12,
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _add_footer(canvas_obj, doc):
    """Add footer to each page."""
    add_header_footer(canvas_obj, doc)


def create_cover_page():
    """Create the cover page flowable."""
    elements = []
    add_cover_page(elements, "QUARTERLY REVIEW", QUARTER_NAME, SALES_ASSOCIATE)
    return elements


def create_quarter_at_glance():
    """Create the 'Quarter at a Glance' dashboard page."""
    elements = []

    elements.append(Paragraph("QUARTER AT A GLANCE", heading_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Key Metrics Table
    metrics_data = [
        ["Metric", "Value"],
        ["Quarter Revenue", f"${QUARTER_REVENUE:,.0f}"],
        ["Deals Closed This Quarter", str(DEALS_CLOSED_THIS_QUARTER)],
        ["Active Pipeline", f"${ACTIVE_PIPELINE_VALUE:,.0f} ({ACTIVE_PIPELINE_COUNT} deals)"],
        ["New Opportunities Created", str(NEW_OPPORTUNITIES_COUNT)],
        ["Meetings Held", str(MEETINGS_HELD_COUNT)],
        ["Pipeline Touches/Week", f"{PIPELINE_TOUCHES_PER_WEEK} deals avg"],
        ["Post-Meeting Follow-Up", f"{POST_MEETING_FOLLOWUP_HOURS} hrs avg"],
    ]

    metrics_table = Table(metrics_data, colWidths=[3.5 * inch, 2 * inch])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SRED_DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), SRED_LIGHT_GRAY),
        ("GRID", (0, 0), (-1, -1), 1, SRED_GRAY),
        ("FONTSIZE", (0, 1), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, SRED_LIGHT_GRAY]),
    ]))

    elements.append(metrics_table)
    elements.append(Spacer(1, 0.3 * inch))

    # YTD Progress Section
    ytd_percentage = (YTD_NEW_BUSINESS_ACTUAL / YTD_NEW_BUSINESS_TARGET) * 100
    deals_percentage = (YTD_DEALS_ACTUAL / YTD_DEALS_TARGET) * 100
    quarterly_percentage = (QUARTERLY_ACTUAL / QUARTERLY_TARGET) * 100 if QUARTERLY_TARGET > 0 else 0

    ytd_data = [
        ["Metric", "Target", "Actual", "Progress"],
        ["YTD New Business", f"${YTD_NEW_BUSINESS_TARGET:,.0f}", f"${YTD_NEW_BUSINESS_ACTUAL:,.0f}", f"{ytd_percentage:.0f}%"],
        ["YTD Deals Closed", str(YTD_DEALS_TARGET), str(YTD_DEALS_ACTUAL), f"{deals_percentage:.0f}%"],
        ["Quarterly Target", f"${QUARTERLY_TARGET:,.0f}", f"${QUARTERLY_ACTUAL:,.0f}", f"{quarterly_percentage:.0f}%"],
    ]

    ytd_table = Table(ytd_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
    ytd_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SRED_LIGHT_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), white),
        ("GRID", (0, 0), (-1, -1), 1, SRED_GRAY),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
    ]))

    elements.append(KeepTogether([
        Paragraph("QUARTER VS TARGET", heading_style),
        Spacer(1, 0.1 * inch),
        ytd_table,
    ]))

    return elements


def create_revenue_trend_page():
    """Create the Revenue Trend page with chart and table."""
    elements = []

    elements.append(Paragraph("REVENUE TREND", heading_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Create matplotlib chart
    fig, ax = plt.subplots(figsize=(6.5, 3.5), dpi=100)

    months = [m["month"] for m in MONTHLY_DATA]
    revenues = [m["revenue"] for m in MONTHLY_DATA]

    bars = ax.bar(months, revenues, color="#40BAEB", alpha=0.8, edgecolor="#2F2A4F", linewidth=1.5)

    # Add target line (quarterly target / 3 for monthly average)
    monthly_target = QUARTERLY_TARGET / 3
    ax.axhline(y=monthly_target, color="#B7DB41", linestyle="--", linewidth=2, label=f"Target (${monthly_target:,.0f}/mo)")

    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))

    ax.set_ylabel("Revenue ($)", fontsize=10)
    ax.set_title("Monthly Revenue vs Quarterly Target", fontsize=12, color="#2F2A4F", fontweight="bold")
    ax.legend(loc="upper left", frameon=True, fancybox=False)
    ax.set_ylim(0, max(revenues + [monthly_target]) * 1.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    chart_path = OUTPUT_PATH / "chart_revenue_trend.png"
    plt.savefig(chart_path, dpi=100, bbox_inches="tight", facecolor="white")
    plt.close()

    # Add chart to PDF
    elements.append(Image(str(chart_path), width=6.5 * inch, height=3.5 * inch))
    elements.append(Spacer(1, 0.2 * inch))

    # Revenue breakdown table
    revenue_data = [["Month", "Revenue", "Deals Won", "Pipeline Change"]]
    for m in MONTHLY_DATA:
        revenue_data.append([
            m["month"],
            f"${m['revenue']:,.0f}",
            str(m["deals"]),
            f"+{m['pipeline_change']}" if m["pipeline_change"] >= 0 else str(m["pipeline_change"])
        ])

    revenue_table = Table(revenue_data, colWidths=[1.8 * inch, 1.6 * inch, 1.4 * inch, 1.6 * inch])
    revenue_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SRED_DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), white),
        ("GRID", (0, 0), (-1, -1), 1, SRED_GRAY),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, SRED_LIGHT_GRAY]),
    ]))

    elements.append(revenue_table)

    return elements


def create_pipeline_health_page():
    """Create the Pipeline Health page with funnel visualization."""
    elements = []

    elements.append(Paragraph("PIPELINE HEALTH", heading_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Create funnel chart
    fig, ax = plt.subplots(figsize=(6.5, 3.5), dpi=100)

    stages = [s["stage"] for s in PIPELINE_STAGES]
    values = [s["value"] for s in PIPELINE_STAGES]
    counts = [s["count"] for s in PIPELINE_STAGES]

    # Create horizontal bars (simple representation of funnel)
    y_pos = range(len(stages))
    bars = ax.barh(y_pos, values, color="#40BAEB", alpha=0.8, edgecolor="#2F2A4F", linewidth=1.5)

    # Add count labels on bars
    for i, (bar, count) in enumerate(zip(bars, counts)):
        width = bar.get_width()
        ax.text(width / 2, bar.get_y() + bar.get_height() / 2, f"{count} deals",
                ha="center", va="center", fontsize=9, fontweight="bold", color="white")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(stages, fontsize=9)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))
    ax.set_xlabel("Pipeline Value ($)", fontsize=10)
    ax.set_title("Current Pipeline by Stage", fontsize=12, color="#2F2A4F", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    plt.tight_layout()
    funnel_path = OUTPUT_PATH / "chart_pipeline_funnel.png"
    plt.savefig(funnel_path, dpi=100, bbox_inches="tight", facecolor="white")
    plt.close()

    # Add chart
    elements.append(Image(str(funnel_path), width=6.5 * inch, height=3.5 * inch))
    elements.append(Spacer(1, 0.2 * inch))

    # Pipeline summary table
    pipeline_data = [["Stage", "Deals", "Total Value", "Avg Deal Size"]]
    for stage in PIPELINE_STAGES:
        avg_deal = stage["value"] / stage["count"] if stage["count"] > 0 else 0
        pipeline_data.append([
            stage["stage"],
            str(stage["count"]),
            f"${stage['value']:,.0f}",
            f"${avg_deal:,.0f}"
        ])

    pipeline_table = Table(pipeline_data, colWidths=[1.8 * inch, 1.2 * inch, 1.8 * inch, 1.8 * inch])
    pipeline_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SRED_DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), white),
        ("GRID", (0, 0), (-1, -1), 1, SRED_GRAY),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, SRED_LIGHT_GRAY]),
    ]))

    elements.append(pipeline_table)

    return elements


def create_marketing_snapshot_page():
    """Create the Marketing Snapshot page — outbound metrics across all channels."""
    elements = []

    elements.append(Paragraph("MARKETING SNAPSHOT", heading_style))
    elements.append(Spacer(1, 0.15 * inch))

    # Summary text
    summary_style = ParagraphStyle(
        "MarketingSummary",
        parent=styles["BodyText"],
        fontSize=10,
        fontName=BODY_FONT,
        leading=13,
        textColor=SRED_GRAY,
    )
    elements.append(Paragraph(
        "Outbound performance across all channels: Prospecting Agent email sequences, "
        "Evan's personal emails, and LinkedIn (HeyReach). Data pulled from HubSpot and HeyReach.",
        summary_style
    ))
    elements.append(Spacer(1, 0.15 * inch))

    # --- Email Outbound Section ---
    sub_heading = ParagraphStyle(
        "MktSubHead",
        parent=styles["Normal"],
        fontSize=12,
        textColor=SRED_DARK_BLUE,
        fontName=HEADING_FONT,
        spaceAfter=6
    )
    email_outbound_header = Paragraph("EMAIL OUTBOUND", sub_heading)

    email_data = [
        ["Channel", "Sent", "Replies", "Reply Rate", "Meetings Booked"],
        [
            "Prospecting Agent (automated)",
            f"{PROSPECTING_EMAILS_SENT:,}",
            str(PROSPECTING_REPLIES_RECEIVED),
            f"{PROSPECTING_REPLY_RATE}%",
            str(PROSPECTING_MEETINGS_BOOKED),
        ],
        [
            "Evan (personal)",
            str(EVAN_PERSONAL_EMAILS_SENT),
            str(int(EVAN_PERSONAL_EMAILS_SENT * EVAN_PERSONAL_REPLY_RATE / 100)),
            f"{EVAN_PERSONAL_REPLY_RATE}%",
            "—",
        ],
    ]

    email_table = Table(email_data, colWidths=[2 * inch, 0.8 * inch, 0.8 * inch, 1 * inch, 1.2 * inch])
    email_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SRED_LIGHT_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), HEADING_FONT if HEADING_FONT != 'Helvetica-Bold' else "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), white),
        ("GRID", (0, 0), (-1, -1), 0.5, SRED_LIGHT_GRAY),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("FONTNAME", (0, 1), (-1, -1), BODY_FONT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, SRED_LIGHT_GRAY]),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    ]))
    elements.append(KeepTogether([email_outbound_header, email_table]))
    elements.append(Spacer(1, 0.2 * inch))

    # --- LinkedIn Outbound Section ---
    linkedin_outbound_header = Paragraph("LINKEDIN OUTBOUND (HEYREACH)", sub_heading)

    linkedin_data = [
        ["Metric", "This Quarter", "All-Time"],
        ["Connections Sent", str(LINKEDIN_CONNECTIONS_SENT), "2,050"],
        ["Connections Accepted", str(LINKEDIN_CONNECTIONS_ACCEPTED), f"358 ({17.5}%)"],
        ["Acceptance Rate", f"{LINKEDIN_ACCEPTANCE_RATE}%", "17.5%"],
        ["Messages Sent", str(LINKEDIN_MESSAGES_SENT), "417"],
        ["Message Reply Rate", f"{LINKEDIN_MESSAGES_REPLY_RATE}%", "25.7%"],
        ["InMails Sent", str(LINKEDIN_INMAILS_SENT), "864"],
        ["InMail Reply Rate", f"{LINKEDIN_INMAIL_REPLY_RATE}%", "5.8%"],
    ]

    linkedin_table = Table(linkedin_data, colWidths=[2.2 * inch, 1.6 * inch, 1.8 * inch])
    linkedin_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SRED_LIGHT_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), HEADING_FONT if HEADING_FONT != 'Helvetica-Bold' else "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), white),
        ("GRID", (0, 0), (-1, -1), 0.5, SRED_LIGHT_GRAY),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("FONTNAME", (0, 1), (-1, -1), BODY_FONT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, SRED_LIGHT_GRAY]),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    ]))
    elements.append(KeepTogether([linkedin_outbound_header, linkedin_table]))
    elements.append(Spacer(1, 0.2 * inch))

    # --- Channel Comparison Chart ---
    fig, ax = plt.subplots(figsize=(6.5, 3), dpi=100)

    channels = ['Prospecting\nAgent', 'Evan\nPersonal', 'LinkedIn\nMessages', 'LinkedIn\nInMails']
    reply_rates = [PROSPECTING_REPLY_RATE, EVAN_PERSONAL_REPLY_RATE, LINKEDIN_MESSAGES_REPLY_RATE, LINKEDIN_INMAIL_REPLY_RATE]
    bar_colors = ['#40BAEB', '#35B586', '#B7DB41', '#2F2A4F']

    bars = ax.bar(channels, reply_rates, color=bar_colors, edgecolor='white', linewidth=1)

    for bar, rate in zip(bars, reply_rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{rate}%', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#2F2A4F')

    ax.set_ylabel('Reply Rate (%)', fontsize=10, color='#2F2A4F')
    ax.set_title('Reply Rate by Channel', fontsize=12, color='#2F2A4F', fontweight='bold')
    ax.set_ylim(0, max(reply_rates) * 1.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    chart_path = OUTPUT_PATH / "chart_marketing_channels.png"
    plt.savefig(chart_path, dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()

    elements.append(Image(str(chart_path), width=6 * inch, height=2.8 * inch))
    elements.append(Spacer(1, 0.15 * inch))

    # Key Insight
    insight_style = ParagraphStyle(
        "MktInsight",
        parent=styles["BodyText"],
        fontSize=10,
        fontName=BODY_FONT,
        leading=13,
        textColor=SRED_GRAY,
    )
    elements.append(Paragraph(
        f"<b>Key Insight:</b> LinkedIn messages ({LINKEDIN_MESSAGES_REPLY_RATE}% reply) and Evan's personal emails "
        f"({EVAN_PERSONAL_REPLY_RATE}% reply) dramatically outperform automated sequences ({PROSPECTING_REPLY_RATE}%) "
        f"and InMails ({LINKEDIN_INMAIL_REPLY_RATE}%). Volume vs. quality tradeoff — the Prospecting Agent drives "
        f"awareness at scale while personal touches convert.",
        insight_style
    ))

    return elements


def create_coaching_progress_page():
    """Create the Coaching Progress page with SDT tracking."""
    elements = []

    elements.append(Paragraph("COACHING PROGRESS", heading_style))
    elements.append(Spacer(1, 0.15 * inch))

    # Coaching sessions
    sessions_text = f"<b>Coaching Sessions This Quarter:</b> {COACHING_SESSIONS_THIS_QUARTER} weekly sessions"
    elements.append(Paragraph(sessions_text, body_style))
    elements.append(Spacer(1, 0.15 * inch))

    # Skill focus areas
    skill_header = Paragraph("Skill Focus Areas", ParagraphStyle(
        "SubHeading",
        parent=styles["Normal"],
        fontSize=11,
        textColor=SRED_DARK_BLUE,
        fontName="Helvetica-Bold",
        spaceAfter=6
    ))
    elements.append(KeepTogether([
        skill_header,
        Paragraph("• Primary: Follow-up discipline", body_style),
        Paragraph("• Secondary: Talk ratio awareness", body_style),
    ]))
    elements.append(Spacer(1, 0.15 * inch))

    # SDT Progress Table
    sdt_progress_header = Paragraph("Self-Determination Theory (SDT) Progress", ParagraphStyle(
        "SubHeading",
        parent=styles["Normal"],
        fontSize=11,
        textColor=SRED_DARK_BLUE,
        fontName="Helvetica-Bold",
        spaceAfter=6
    ))

    sdt_data = [
        ["Dimension", "Start of Quarter", "End of Quarter", "Trend"],
        ["Autonomy", SDT_BASELINE["autonomy"], SDT_CURRENT["autonomy"], "→"],
        ["Competence", SDT_BASELINE["competence"], SDT_CURRENT["competence"], "↑"],
        ["Relatedness", SDT_BASELINE["relatedness"], SDT_CURRENT["relatedness"], "↑"],
    ]

    sdt_table = Table(sdt_data, colWidths=[1.6 * inch, 1.8 * inch, 1.8 * inch, 0.6 * inch])
    sdt_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SRED_GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (3, 0), (3, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), white),
        ("GRID", (0, 0), (-1, -1), 1, SRED_GRAY),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, SRED_LIGHT_GRAY]),
    ]))

    elements.append(KeepTogether([sdt_progress_header, sdt_table]))
    elements.append(Spacer(1, 0.15 * inch))

    # Key Behavioral Metrics
    behavioral_header = Paragraph("Key Behavioral Metrics (Quarter Comparison)", ParagraphStyle(
        "SubHeading",
        parent=styles["Normal"],
        fontSize=11,
        textColor=SRED_DARK_BLUE,
        fontName="Helvetica-Bold",
        spaceAfter=6
    ))

    metrics_data = [["Metric", "Baseline", "This Quarter", "Change"]]
    for m in BEHAVIORAL_METRICS:
        metrics_data.append([m["metric"], m["baseline"], m["current"], m["change"]])

    metrics_table = Table(metrics_data, colWidths=[1.8 * inch, 1.4 * inch, 1.4 * inch, 1 * inch])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), SRED_DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (3, 0), (3, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), white),
        ("GRID", (0, 0), (-1, -1), 1, SRED_GRAY),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, SRED_LIGHT_GRAY]),
    ]))

    elements.append(KeepTogether([behavioral_header, metrics_table]))

    return elements


def create_commitments_page():
    """Create the Commitments & Next Quarter Preview page."""
    elements = []

    elements.append(Paragraph("COMMITMENTS & NEXT QUARTER", heading_style))
    elements.append(Spacer(1, 0.2 * inch))

    # This Quarter's Review
    commitments_review_header = Paragraph("This Quarter's Commitments Review", ParagraphStyle(
        "SubHeading",
        parent=styles["Normal"],
        fontSize=11,
        textColor=SRED_DARK_BLUE,
        fontName="Helvetica-Bold",
        spaceAfter=6
    ))

    commitment_text = """
    • Follow-up within 24 hours of discovery calls: <b>Met</b><br/>
    • Achieve 25% win rate on technical discovery stage: <b>Partially Met (18.5%)</b><br/>
    • Reduce average sales cycle to 85 days: <b>Met (87 days)</b><br/>
    • Increase talk ratio awareness in pitch meetings: <b>Met (6-8%)</b>
    """
    elements.append(KeepTogether([commitments_review_header, Paragraph(commitment_text, body_style)]))
    elements.append(Spacer(1, 0.2 * inch))

    # Next Quarter Preview
    next_quarter_header = Paragraph("Next Quarter Focus (FY2027 Q1 — May 1 - July 31, 2026)", ParagraphStyle(
        "SubHeading",
        parent=styles["Normal"],
        fontSize=11,
        textColor=SRED_DARK_BLUE,
        fontName="Helvetica-Bold",
        spaceAfter=6
    ))

    next_quarter_text = """
    <b>Primary Focus:</b> Discovery depth and strategic questioning<br/>
    <b>Secondary Focus:</b> Pipeline velocity (reduce sales cycle to 75 days)<br/>
    <b>SDT Goal:</b> Move Autonomy to Independent; maintain Competence and Relatedness<br/>
    <b>Revenue Target:</b> $100,000 (increased from $75,000 base)<br/>
    <b>Deal Target:</b> 3-4 deals closed<br/>
    <b>Pipeline Health:</b> Maintain 10+ active deals in pipeline
    """
    elements.append(KeepTogether([next_quarter_header, Paragraph(next_quarter_text, body_style)]))
    elements.append(Spacer(1, 0.2 * inch))

    # Manager Notes
    manager_notes_header = Paragraph("Manager Notes", ParagraphStyle(
        "SubHeading",
        parent=styles["Normal"],
        fontSize=11,
        textColor=SRED_DARK_BLUE,
        fontName="Helvetica-Bold",
        spaceAfter=6
    ))

    notes_text = """
    <i>This section is reserved for strategic observations from Jude or the coaching team.
    Update quarterly as coaching progress is monitored and trends emerge.</i>
    """
    elements.append(KeepTogether([manager_notes_header, Paragraph(notes_text, body_style)]))

    return elements


def create_personal_goals_page():
    """Create the Personal Goals page — Evan + Coach ONLY.

    This page is NOT included in the manager summary.
    Set INCLUDE_PERSONAL_GOALS = False to exclude it.
    """
    elements = []

    elements.append(Paragraph("PERSONAL GOALS", heading_style))
    elements.append(Spacer(1, 0.05 * inch))

    # Privacy banner
    banner_data = [["This page is between Evan and the coach only. It is not included in the Manager Summary."]]
    banner = Table(banner_data, colWidths=[6.5 * inch])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SRED_LIGHT_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, -1), white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), BODY_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(banner)
    elements.append(Spacer(1, 0.15 * inch))

    goal_title_style = ParagraphStyle(
        "GoalTitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=SRED_DARK_BLUE,
        fontName=HEADING_FONT,
        spaceAfter=4,
    )

    goal_body_style = ParagraphStyle(
        "GoalBody",
        parent=styles["BodyText"],
        fontSize=9,
        fontName=BODY_FONT,
        leading=12,
        textColor=SRED_GRAY,
    )

    status_colors = {
        "Not Started": SRED_LIGHT_GRAY,
        "In Progress": SRED_LIGHT_BLUE,
        "On Track": SRED_GREEN,
        "At Risk": SRED_ORANGE,
        "Complete": SRED_EMERALD,
    }

    for i, goal in enumerate(PERSONAL_GOALS, 1):
        # Goal header with status badge
        goal_header = Paragraph(f"GOAL {i}: {goal['title'].upper()}", goal_title_style)

        # Status and progress
        status_color = status_colors.get(goal["status"], SRED_LIGHT_GRAY)
        progress = goal.get("progress_pct", 0)

        status_data = [
            ["Status", "Progress", "Target Date"],
            [goal["status"], f"{progress}%", goal.get("timebound", "—")],
        ]
        status_table = Table(status_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
        status_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), status_color),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), HEADING_FONT if HEADING_FONT != 'Helvetica-Bold' else "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTNAME", (0, 1), (-1, -1), BODY_FONT),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, SRED_LIGHT_GRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("BACKGROUND", (0, 1), (-1, -1), white),
        ]))
        elements.append(KeepTogether([goal_header, status_table]))
        elements.append(Spacer(1, 0.05 * inch))

        # SMART breakdown
        smart_data = [
            ["S — Specific", goal.get("specific", "—")],
            ["M — Measurable", goal.get("measurable", "—")],
            ["A — Achievable", goal.get("achievable", "—")],
            ["R — Relevant", goal.get("relevant", "—")],
            ["T — Time-bound", goal.get("timebound", "—")],
        ]
        smart_table = Table(smart_data, colWidths=[1.5 * inch, 4.5 * inch])
        smart_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), HEADING_FONT if HEADING_FONT != 'Helvetica-Bold' else "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), BODY_FONT),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TEXTCOLOR", (0, 0), (0, -1), SRED_LIGHT_BLUE),
            ("TEXTCOLOR", (1, 0), (1, -1), SRED_GRAY),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, SRED_LIGHT_GRAY),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [white, SRED_LIGHT_GRAY]),
        ]))
        elements.append(smart_table)
        elements.append(Spacer(1, 0.05 * inch))

        # Coach notes
        if goal.get("coach_notes"):
            elements.append(Paragraph(
                f"<b>Coach Notes:</b> {goal['coach_notes']}", goal_body_style
            ))

        elements.append(Spacer(1, 0.15 * inch))

    # Quarterly reflection prompts
    elements.append(Spacer(1, 0.1 * inch))
    reflection_heading = ParagraphStyle(
        "ReflectionHead",
        parent=styles["Normal"],
        fontSize=11,
        textColor=SRED_DARK_BLUE,
        fontName=HEADING_FONT,
        spaceAfter=6,
    )
    reflection_header = Paragraph("QUARTERLY REFLECTION", reflection_heading)

    reflection_prompts = [
        "Which goal gave you the most energy this quarter? Why?",
        "What got in the way of the goals that stalled?",
        "Is there a goal you want to carry forward, modify, or let go of?",
        "What's one thing outside of work that, if you made progress on it next quarter, would make you feel great?",
    ]
    reflection_items = [Paragraph(f"• {prompt}", goal_body_style) for prompt in reflection_prompts]
    elements.append(KeepTogether([reflection_header] + reflection_items))

    return elements


# ============================================================================
# MAIN DOCUMENT GENERATION
# ============================================================================

def generate_quarterly_report():
    """Generate the complete quarterly review PDF."""

    doc = SimpleDocTemplate(
        str(PDF_FILENAME),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        onFirstPage=_add_footer,
        onLaterPages=_add_footer,
    )

    # Build the story (flowables)
    story = []

    # Page 1: Cover
    story.extend(create_cover_page())
    story.append(PageBreak())

    # Page 2: Quarter at a Glance
    story.extend(create_quarter_at_glance())
    story.append(PageBreak())

    # Page 3: Revenue Trend
    story.extend(create_revenue_trend_page())
    story.append(PageBreak())

    # Page 4: Pipeline Health
    story.extend(create_pipeline_health_page())
    story.append(PageBreak())

    # Page 5: Marketing Snapshot
    story.extend(create_marketing_snapshot_page())
    story.append(PageBreak())

    # Page 6: Coaching Progress
    story.extend(create_coaching_progress_page())
    story.append(PageBreak())

    # Page 7: Commitments & Next Quarter
    story.extend(create_commitments_page())

    # Page 8: Personal Goals (Evan + Coach ONLY — set INCLUDE_PERSONAL_GOALS = False for manager version)
    if INCLUDE_PERSONAL_GOALS:
        story.append(PageBreak())
        story.extend(create_personal_goals_page())

    # Build the PDF
    doc.build(story)

    print(f"\n✓ Quarterly Review PDF generated successfully!")
    print(f"  Location: {PDF_FILENAME}")
    print(f"  Quarter: {QUARTER_NAME} ({QUARTER_START_DATE} – {QUARTER_END_DATE})")
    print(f"  Sales Associate: {SALES_ASSOCIATE}")
    print(f"  Revenue: ${QUARTER_REVENUE:,.0f}")
    print(f"\nConfiguration variables are clearly labeled in the script header.")
    print("Update them for each quarter before running the script.")


if __name__ == "__main__":
    generate_quarterly_report()
