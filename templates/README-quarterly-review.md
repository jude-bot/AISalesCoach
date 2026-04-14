# Quarterly Review Report Generator

## Overview

`quarterly-review-template.py` is a Python script that generates a professional 6-page PDF quarterly review report for SRED.ca's sales coaching program. The report includes:

- **Page 1:** Cover page with quarter info and sales associate name
- **Page 2:** Quarter at a Glance dashboard with KPIs and YTD progress
- **Page 3:** Revenue trend analysis with monthly breakdown and chart
- **Page 4:** Pipeline health funnel visualization and stage breakdown
- **Page 5:** Coaching progress with SDT tracking and behavioral metrics
- **Page 6:** Commitments review and next quarter preview

## Requirements

The script automatically installs missing dependencies:
- `reportlab` — PDF generation
- `matplotlib` — Chart rendering

## Configuration

All input data is controlled by clearly labeled configuration variables at the top of the script (lines 37-109):

### Key Configuration Variables

```python
# Quarter identification
QUARTER_NAME = "FY2026 Q4"
QUARTER_START_DATE = "February 1, 2026"
QUARTER_END_DATE = "April 30, 2026"
SALES_ASSOCIATE = "Evan Batchelor"

# Revenue & pipeline data
QUARTER_REVENUE = 185923
ACTIVE_PIPELINE_VALUE = 130000
DEALS_CLOSED_THIS_QUARTER = 1

# Monthly breakdown
MONTHLY_DATA = [
    {"month": "Feb 2026", "revenue": 72246, "deals": 0, "pipeline_change": 2},
    {"month": "Mar 2026", "revenue": 113677, "deals": 1, "pipeline_change": 1},
    {"month": "Apr 2026 (7 days)", "revenue": 0, "deals": 1, "pipeline_change": 3},
]

# Pipeline stages
PIPELINE_STAGES = [
    {"stage": "Opportunity", "count": 5, "value": 70000},
    {"stage": "Assessment", "count": 1, "value": 15000},
    # ... etc
]

# SDT progress
SDT_BASELINE = {"autonomy": "Developing", "competence": "Strong Foundation", "relatedness": "Natural Strength"}
SDT_CURRENT = {"autonomy": "Developing→Independent", "competence": "Strong", "relatedness": "Strong"}

# Behavioral metrics
BEHAVIORAL_METRICS = [
    {"metric": "Talk Ratio", "baseline": "4-6%", "current": "6-8%", "change": "↑"},
    # ... etc
]
```

## Usage

### Run the script

```bash
python3 quarterly-review-template.py
```

Output: `/sessions/ecstatic-eloquent-hamilton/mnt/sales-coach/outputs/quarterly-review-FY2026-Q4-draft.pdf`

### For a new quarter

1. Update the configuration variables at the top of the script
2. Gather data from:
   - **Fireflies:** Meeting count and transcripts
   - **HubSpot:** Pipeline stages, deal values, win rate
   - **Gmail:** Email activity summary
   - **HeyReach:** LinkedIn outreach metrics
   - **Coaching sessions:** SDT progress and behavioral metrics from weekly session notes
3. Plug numbers into the config variables
4. Run the script
5. PDF is generated automatically

## Data Sources

| Data | Source | Method |
|------|--------|--------|
| Meetings held | Fireflies MCP | Query transcripts for date range |
| Revenue, deals, pipeline | HubSpot API | Search deals by close date / stage |
| YTD progress | HubSpot + QuickBooks | Rolling sum of closed deals |
| LinkedIn metrics | HeyReach browser | Dashboard or API (if available) |
| SDT/behavioral progress | Weekly coaching notes | Manual entry into config |

## Brand Design

The script uses SRED.ca brand colors throughout:
- SRED_BLUE = #1a365d (headings, tables, primary)
- SRED_LIGHT_BLUE = #2b6cb0 (charts, accents)
- SRED_GREEN = #38a169 (positive indicators, SDT section)
- SRED_ORANGE = #dd6b20 (target lines, watch items)
- SRED_RED = #e53e3e (alerts, behind status)
- SRED_GRAY = #718096 (secondary text)
- SRED_LIGHT_GRAY = #edf2f7 (table backgrounds)

Body font: Helvetica 10pt (ReportLab default)
Headings: Helvetica-Bold in SRED_BLUE

## Page Structure Detail

### Page 1: Cover
- Centered title "SRED.ca Sales Coaching"
- Subtitle "Quarterly Review: [QUARTER_NAME]"
- Date range
- Sales associate name

### Page 2: Quarter at a Glance
- KPI metrics table (revenue, deals, pipeline, meetings, follow-up rate, LinkedIn activity)
- YTD progress section with target vs actual comparisons
- Progress bars showing % of target

### Page 3: Revenue Trend
- Bar chart: Monthly revenue vs. quarterly target line
- Monthly breakdown table: revenue, deals won, pipeline change

### Page 4: Pipeline Health
- Horizontal funnel chart showing pipeline by stage
- Stage summary table: count, value, average deal size

### Page 5: Coaching Progress
- Number of coaching sessions this quarter
- Skill focus areas
- SDT progress table (Autonomy, Competence, Relatedness)
- Behavioral metrics with baseline → current comparisons

### Page 6: Commitments & Next Quarter
- This quarter's commitments with Met/Partially Met/Not Met status
- Next quarter focus areas (primary, secondary, SDT goals, revenue/deal targets)
- Manager notes section for Jude's observations

## Customization

The script is modular. To modify:

- **Page layout:** Edit `create_*_page()` functions
- **Chart style:** Modify matplotlib calls in revenue/pipeline functions
- **Colors:** Update `SRED_*` color constants
- **Table styling:** Edit `TableStyle()` calls
- **Font:** Change `fontName` parameters (defaults to Helvetica)

## Notes

- Charts are saved as PNG files in the outputs folder (used in the PDF)
- Footer with page number and "SRED.ca | Quarterly Review" is auto-added to all pages
- All monetary values are formatted as currency (e.g., $185,923)
- Percentages and metrics use trend arrows (↑, ↓, →)

## Troubleshooting

**Helvetica font warnings:** These are harmless — ReportLab will use a fallback font. To fix, install Helvetica system-wide or ignore the warnings.

**Missing data fields:** Edit the corresponding configuration variable and re-run.

**PDF not generated:** Check console output for errors. Most commonly: file path permissions or missing pandas/numpy dependencies.
