# Pre-Session Brief Template

> This document defines the data gathering and synthesis format used to prepare the AI coach before each weekly VAPI session. The brief gives the coach full context on the past week's sales activity so it can coach with specificity, not generalities.

## Date Window — Critical Rule

**The prep task runs at 6:00 AM every Monday.**

The reporting window is always the **prior calendar week: Monday 00:00:00 → Sunday 23:59:59** (local time, Eastern).

This is NOT a rolling 7-day window. It is a fixed Mon-Sun calendar week. This matters because:
- It's consistent and auditable — "the week of April 7-13" means the same thing every time
- It prevents data from bleeding across coaching sessions
- HeyReach, HubSpot, Fireflies, and Gmail all use the same window

**How to calculate the window at runtime:**
```
today = Monday (task run date)
week_start = today - 7 days  → prior Monday at 00:00:00
week_end   = today - 1 day   → prior Sunday at 23:59:59

Example: task runs Monday April 14, 2026
  week_start = Monday April 7, 2026 00:00:00 ET
  week_end   = Sunday April 13, 2026 23:59:59 ET
```

All four data sources must be filtered to this exact window. Do not use "last 7 days" shortcuts.

---

## Data Gathering Steps

### 1. Fireflies — Meeting Transcripts

**Tool:** `fireflies_get_transcripts` with `participants: ["evan@sred.ca"]`, `fromDate` = prior Monday 00:00:00, `toDate` = prior Sunday 23:59:59, `format: "json"`

> **Date filter:** Include only meetings where the recorded date falls within the prior calendar week window. Meetings that started before Monday 00:00 or after Sunday 23:59 are excluded, even if they appear in a broader pull.

**Then for each meeting:** `fireflies_get_transcript` with the meeting ID

**Classify each meeting into one of three types:**

| Type | How to Identify | What to Evaluate |
|------|----------------|------------------|
| **Pitch** | Evan organized, external prospect(s), title contains "SRED.ca", "Claim Overview", "SR&ED Conversation", or generic "Meeting with SRED.ca" / "Meeting with Bloom Technical". Evan's talk ratio should be >50%. | Full Barrows evaluation: discovery quality, pitch structure, objection handling, urgency creation, close attempt, next-step setting |
| **Discovery / Handoff** | Both Evan and Logan/James present, external prospect(s). Typically a second meeting where tech lead takes over. | Evan's intro clarity, confidence when explaining contract/pricing, smooth handoff, whether he stays engaged or checks out |
| **Technical Interview** | Logan or James organized, existing client. Evan may be on the call but is not the focus. | Only flag if Evan speaks — assess confidence and clarity on business/contract topics. Otherwise skip for coaching purposes. |

**For each Pitch or Discovery meeting, extract:**

```
Meeting: [Title]
Date: [Date]
Duration: [X] minutes
Prospect: [Name, Company, Email]
Meeting Type: Pitch | Discovery/Handoff | Technical Interview

--- Speaker Analysis ---
Evan: [X] lines ([Y]% of conversation)
Prospect: [X] lines ([Y]%)
Logan/James: [X] lines ([Y]%) (if present)

--- Summary ---
[Fireflies short_summary]

--- Key Moments (from transcript) ---
1. [Timestamp/context] — [Notable moment: strong discovery question, missed opportunity, good objection handling, etc.]
2. ...

--- Action Items (Evan's only) ---
[From Fireflies action_items, filtered to Evan]

--- Coaching Flags ---
- [ ] Discovery depth: Did Evan ask about the prospect's business before pitching?
- [ ] Urgency: Did Evan help the prospect understand cost of inaction / deadline pressure?
- [ ] Personalization: Was the pitch tailored to this specific prospect, or generic?
- [ ] Next steps: Were clear, specific next steps set before ending the call?
- [ ] Talk ratio: Is Evan talking more than 60% on a pitch? (ideal: 40-50% — prospect should talk more)
- [ ] Small talk management: How long before business starts? (>5 min = flag)
```

### 2. HubSpot — Pipeline & CRM Activity

**Tools:** Via SRED Weekly Prospecting skill's HubSpot integration (browser automation or API)

**Date filter:** All deal activity, email logs, tasks, and contact creation must be filtered to the prior calendar week window (Monday 00:00 → Sunday 23:59). Use HubSpot's `hs_timestamp`, `createdate`, or `notes_last_contacted` properties as appropriate for each object type. Deal stage changes are tracked by `hs_date_entered_[stage]` — compare to window to identify movement during the week.

**Pull:**

```
--- Pipeline Snapshot ---
Total active deals: [X]
Total pipeline value: $[X]

--- Deal Movement This Week ---
| Deal | Company | Stage Change | Value | Days in Stage | Flag |
|------|---------|-------------|-------|---------------|------|
| ... | ... | Prospect → Qualified | $15K | 3 | ✅ Moving |
| ... | ... | No change | $15K | 45 | ⚠️ Stalled |

--- New Contacts Created ---
[Count] new contacts added this week
[List with company, source, and any notes]

--- Tasks ---
Completed: [X]
Overdue: [X]
[List overdue tasks with due dates]

--- Activity Log ---
Calls logged: [X]
Emails logged: [X]
Meetings logged: [X]
```

### 3. Email Follow-Up Tracking

**Primary source:** HubSpot CRM (`search_crm_objects` with `objectType: "emails"`) — pulls all logged email activity for Evan's contacts. Confirmed working 2026-04-07.
**Secondary source:** Gmail MCP (`gmail_search_messages`) — only sees emails where Jude is on the thread (CC'd, forwarded, or direct). Cannot see Evan's direct prospect emails.

> **NOTE:** Gmail MCP is authenticated as jude@sred.ca. Even with Google Workspace admin status, the Gmail API only searches the authenticated user's mailbox. Domain-wide delegation at the Google Cloud level would be needed for cross-account access. HubSpot is the reliable source for Evan's email activity.

**HubSpot Query Pattern (confirmed working):**

```
# Step 1: Find the contact ID for a prospect
search_crm_objects(objectType="contacts", query="[prospect name or company]",
  properties=["firstname","lastname","email","company","hubspot_owner_id",
    "hs_sales_email_last_replied","notes_last_contacted"])

# Step 2: Pull all emails for that contact, filtered to Evan (owner 228172981)
search_crm_objects(objectType="emails",
  filterGroups=[{
    "filters": [{"propertyName":"hubspot_owner_id","operator":"EQ","value":"228172981"}],
    "associatedWith": [{"objectType":"contacts","operator":"EQUAL","objectIdValues":[CONTACT_ID]}]
  }],
  properties=["hs_email_subject","hs_email_direction","hs_email_status",
    "hs_timestamp","hs_email_from_email","hs_email_to_email","hubspot_owner_id"],
  sorts=[{"propertyName":"hs_timestamp","direction":"DESCENDING"}])

# Step 3: For email content/body, use get_crm_objects with the email ID
get_crm_objects(objectType="emails", objectIds=[EMAIL_ID],
  properties=["hs_email_subject","hs_email_text","hs_email_html",
    "hs_email_from_email","hs_email_to_email","hs_timestamp"])

# Key reference: Evan's HubSpot owner ID = 228172981
```

**Pull from HubSpot:**

```
--- Post-Meeting Follow-Up Audit ---
[For each meeting this week, check:]
Meeting: [Title] — [Date]
  Follow-up email sent? [Yes / No]
  Time to follow-up: [X hours after meeting]
  Follow-up quality: [See evaluation below]
  Attachments included? [Presentation, prep guide, engagement letter, etc.]

--- Outbound Email Activity ---
Emails sent to prospects: [X]
Emails sent to existing clients: [X]
Average response time to inbound prospect emails: [X hours]
Threads with no reply from prospect (>48 hrs): [List]
Threads with no reply from Evan (prospect replied, Evan hasn't): [List — THIS IS CRITICAL]

--- Notable Threads ---
[For each significant prospect thread:]
- Thread: [Subject] — [Prospect name, company]
  - Stage in pipeline: [Prospect / Qualified / Proposal / etc.]
  - Last action: [Evan sent / Prospect replied / No response]
  - Days since last activity: [X]
  - Flag: [Hot / Needs follow-up / Gone cold / Evan dropped the ball]
```

**Email Evaluation Criteria (John Barrows "Sales-Ready Messaging"):**

The coach should evaluate Evan's emails against these standards:

```
--- Post-Pitch Follow-Up Email (sent same day or next morning after first meeting) ---
- [ ] Timeliness: Sent within 4 hours of meeting end (same business day)
- [ ] Personal touch: References something specific from the conversation (not a template)
- [ ] Recap of value: Restates what SR&ED could mean for THIS specific prospect
- [ ] Clear next steps: Specific action items with owners and timeline
- [ ] Resources attached: Presentation deck, interview prep guide, example project
- [ ] Referral follow-through: If Evan promised an intro (e.g., to Jane, to IRAP), did he include it?
- [ ] Guarantee mention: Includes or links to the SR&ED guarantee
- [ ] Pricing clarity: Restates the fee structure discussed
- [ ] Info request: Asks for company name, fiscal year-end, business number, etc.
- [ ] Professional signature: Proper formatting, booking link, contact info

--- Opportunity Follow-Up (ongoing nurture after initial engagement) ---
- [ ] Cadence consistency: Is Evan following up at regular intervals? (ideal: 3-5 business days between touches)
- [ ] Value-add touches: Is he sharing relevant content, not just "checking in"?
- [ ] Multi-channel: Is he following up via email AND LinkedIn/phone, not just one channel?
- [ ] Persistence without pestering: 3+ follow-ups before going quiet? Or gives up after 1?
- [ ] Dead thread awareness: Has he identified and re-engaged threads that went cold?

--- Client Communication (existing clients) ---
- [ ] Responsiveness: Replies to client questions within 4 business hours
- [ ] Proactive updates: Does he reach out with status updates, or only when asked?
- [ ] Handoff quality: When looping in Logan/James, does he provide context or just forward?
- [ ] Payment/admin follow-through: Does he handle billing/onboarding tasks promptly?

--- Red Flags to Surface ---
- Meeting happened but NO follow-up email within 24 hours
- Prospect replied but Evan hasn't responded in >48 hours
- Deal in pipeline with no email activity in >7 days
- Follow-up email is a generic template with no personalization
- Promised deliverable in meeting (prep guide, intro, proposal) but no evidence it was sent
- Client CC'd Jude because Evan wasn't responding (escalation signal)
```

**Known good example:** Evan's follow-up to Scott Sheldrake / Numbered GameCo (Jan 28, 2026) hits nearly all the criteria — personal touch (coffee invite), referral to Jane Ramachandran included, interview prep guide attached, guarantee explained with link, pricing stated clearly ($10K startup plan), specific info requested (company name, fiscal year-end, business number, web address), engagement letter mentioned, clear next steps. Use this as the benchmark.

**Coachable example:** Evan's follow-up to Yavuz / Blueshift (Feb 27, 2026 — day after meeting) is decent but misses several items: thanks and next-step setup are good, but no guarantee mention, no pricing recap, no specific info request, no reference to anything personal from the conversation. Compare side-by-side with Sheldrake to show Evan the gap.

**Full timeline example (Blueshift) — shows prospecting-to-close cadence:**
1. Nov 14 — Cold outreach (HeyReach/email sequence)
2. Nov 16 — Follow-up #2 (2 days later)
3. Nov 18 — Follow-up #3 (2 days later)
4. [~3 month gap — no activity]
5. Feb 24 — Re-engagement email "Quick SR&ED check"
6. Feb 26 — Pitch meeting (Fireflies transcript available)
7. Feb 27 — Post-meeting follow-up (next day)
8. Mar 19 — "SR&ED Follow-up" (~3 weeks later)

Coach should flag: the 3-month gap between initial outreach and re-engagement, and the 3-week gap between post-meeting follow-up and next touch.

**Date filter for HubSpot email queries:** Filter `hs_timestamp` to the prior calendar week window. Use `BETWEEN` operator with epoch milliseconds for the Monday 00:00:00 and Sunday 23:59:59 boundaries.

**Pull from Gmail (supplementary):**

> **Date filter:** Gmail search uses `after:YYYY/MM/DD before:YYYY/MM/DD` syntax. Set `after` to prior Monday and `before` to the Monday of the current week (i.e., today). Gmail date filters are inclusive of the `after` date and exclusive of the `before` date.

Search `from:evan@sred.ca after:2026/04/07 before:2026/04/14` in Jude's inbox to find:
- Forwarded prospect threads (Evan shares with Jude for visibility)
- Threads where Jude is CC'd (client communication)
- Calendar invites Evan sends (meeting scheduling patterns)

This gives partial visibility but should NOT be the primary email data source.

### 4. HeyReach — LinkedIn Outbound

**Tool:** Browser automation via Claude in Chrome — login at app.heyreach.io using Jude's account

**Date filter:** In the HeyReach dashboard, set the date range filter explicitly to the prior calendar week:
- From: prior Monday (e.g., April 7, 2026)
- To: prior Sunday (e.g., April 13, 2026)
- Sender filter: "Evan Batchelor" (not "All senders")

> Do not rely on HeyReach's default date range. Always set the filter manually to the exact Mon-Sun window before reading any stats. Take a screenshot or read the displayed numbers directly from the filtered dashboard view.

**Pull:**

```
--- LinkedIn Outbound Metrics ---
Connection requests sent: [X]
Connection requests accepted: [X] ([Y]% acceptance rate)
Messages sent: [X]
Replies received: [X] ([Y]% reply rate)
Personalized vs. template messages: [X] / [X]

--- Campaign Performance ---
[If multiple campaigns running:]
| Campaign | Sent | Accepted | Replies | Reply Rate |
|----------|------|----------|---------|------------|
| ... | ... | ... | ... | ... |
```

---

## Brief Synthesis — What the Coach Reads

After gathering all four data sources, synthesize into this structure. This is what gets injected into the VAPI agent's system prompt as context.

```
========================================
WEEKLY SALES COACHING BRIEF
Week of: [Monday date] – [Sunday date]  ← always prior calendar week, never "last 7 days"
Generated: [Monday run date] at 6:00 AM ET
Associate: Evan Batchelor
========================================

📊 WEEK AT A GLANCE
-------------------
Meetings this week: [X] ([Y] pitch, [Z] discovery, [W] technical)
Pipeline deals active: [X] (value: $[X])
Deals moved forward: [X]
Deals stalled (>30 days same stage): [X]
Emails sent to prospects: [X]
LinkedIn messages sent: [X]
Overdue tasks: [X]

Compared to last week: [Better / Worse / Same] — [one-line summary of trend]

🏆 WINS TO OPEN WITH
---------------------
[2-3 specific positive things from the data]
- e.g., "Closed Spearhead — $15K deal, started as a cold outreach in January"
- e.g., "Blueshift moved from Prospect to Qualified after a strong pitch on Feb 26"
- e.g., "LinkedIn acceptance rate up to 35% from 28% last week"

🎙️ MEETING REVIEWS
-------------------
[For each Pitch or Discovery meeting this week, include the full extracted analysis from Step 1]

📈 PIPELINE HEALTH (by stage — see references/stage-specific-evaluation.md)
------------------
Opportunity (Stage 1): [X] deals — [list with days in stage]
SR&ED Assessment (Stage 2): [X] deals — [list with days in stage]
Technical Discovery (Stage 3): [X] deals — [list with days in stage]
Follow-Up (Stage 4): [X] deals — [list with days in stage]
Closed/Won this week: [X] — [list]
Closed/Lost this week: [X] — [list with reason if known]

Deal movement this week:
[Deal movement table from Step 2]

⚠️ Stage health flags:
[Flag any deals stalled >30 days at same stage]
[Flag any deals with no next activity scheduled]
[Flag any deals that moved backward]

💳 PAYMENT GATE CHECK (Assessment → Technical Discovery):
[List any deals at Assessment stage where payment link has been sent]
[Flag any deals where Tech Discovery is scheduled but payment NOT received — process violation]
[Flag any deals with payment link outstanding >7 days with no follow-up]

📧 EMAIL FOLLOW-UP SCORECARD
----------------------------
Post-meeting follow-ups sent this week: [X] of [Y] meetings ([Z]%)
Average time to follow-up: [X hours]
Follow-ups hitting quality bar (see criteria): [X] of [Y]
Prospect replies awaiting Evan's response: [X] — [List]
Deals with no email activity >7 days: [X] — [List]
Cold threads (no activity >14 days, deal still open): [X] — [List]

[For each meeting this week, one-line follow-up status:]
- Think CNC (Apr 6): ✅ Follow-up sent 4hrs later, prep guide attached
- Blueshift (Feb 26): ⚠️ Follow-up sent next day, no prep guide
- Happy Prime (Jan 30): ❌ No follow-up email found

📤 OUTBOUND ASSESSMENT
----------------------
[LinkedIn metrics from Step 4]
[Additional email outbound: cold emails, re-engagement attempts]
[Flag: threads gone cold, prospects not followed up]

🔁 PATTERNS NOTICED
-------------------
[Cross-reference this week's data with previous weeks]
- Recurring strengths: [e.g., "Consistently strong at explaining the SR&ED guarantee"]
- Recurring gaps: [e.g., "Still not asking about timeline/urgency on first calls"]
- Trend: [e.g., "Third week in a row where follow-up emails are delayed >48hrs"]

🎯 RECOMMENDED COACHING FOCUS
-----------------------------
[Pick 1-2 highest-leverage areas based on the data]
[IMPORTANT: Apply stage-specific evaluation criteria — see references/stage-specific-evaluation.md]
[The coach evaluates differently at each stage: outreach quality at Opportunity, discovery depth at Assessment, handoff clarity at Technical Discovery, closing discipline at Follow-Up]
Primary: [Specific skill + why + which stage it applies to, based on evidence]
Secondary: [Specific skill + why + which stage it applies to, based on evidence]

🧠 SDT COACHING NOTES (see references/sdt-coaching-framework.md)
-----------------------------------------------------------------
Motivation language this week: [Obligation ("I should/have to") vs. Alignment ("I want to/believe in")]
Decision Ladder position: [Which rung is coaching operating at? Are we ready to move up?]
Grit/Grace balance (last 3 sessions): [Heavy grit / Balanced / Heavy grace]
SDT need most served this week: [Autonomy / Competence / Relatedness]
SDT need most neglected: [Autonomy / Competence / Relatedness]
Transformational Sales progress: [Is Evan selling mission or mechanism? Which of the Four I's is strongest/weakest?]
SCARF watch: [Any threat responses noticed in recent sessions? Status? Certainty? Autonomy?]

📋 LAST WEEK'S COMMITMENTS
--------------------------
[From previous coaching session output]
1. [Commitment] — [Met / Partially met / Not met] — [Evidence]
   [Was this Evan's own commitment or coach-prescribed?]
2. [Commitment] — [Met / Partially met / Not met] — [Evidence]
   [Was this Evan's own commitment or coach-prescribed?]
```

---

## Classification Logic for Meeting Types

The coach needs to evaluate Evan differently depending on what kind of meeting it is. Here's the decision tree:

```
Is Evan the organizer?
├── YES → Is Logan or James also on the call?
│   ├── YES → Is there an external prospect?
│   │   ├── YES → DISCOVERY/HANDOFF (evaluate: intro, contract explanation, handoff)
│   │   └── NO → INTERNAL (skip for coaching)
│   └── NO → Is there an external prospect?
│       ├── YES → PITCH (full Barrows evaluation)
│       └── NO → INTERNAL (skip for coaching)
└── NO → Is it organized by Logan or James?
    ├── YES → TECHNICAL INTERVIEW (only flag Evan's contributions if any)
    └── NO → EXTERNAL/OTHER (review for context but don't evaluate)
```

## Talk Ratio Benchmarks

| Meeting Type | Evan Target | Why |
|-------------|-------------|-----|
| Pitch (first call) | 50-60% | He's educating, but should be asking enough questions to qualify |
| Pitch (with engaged prospect) | 40-50% | Prospect should be talking more — means better discovery |
| Discovery/Handoff | 15-25% | Logan leads technical; Evan does intro/close |
| Technical Interview | 5-10% | Only speaks on business/contract matters |

## Notes on Data Quality

- **Fireflies speaker attribution** is imperfect — "The Kotamarti Group" was used instead of the person's name when their display name was a company. The coach should not penalize Evan for attribution weirdness.
- **Meeting titles are inconsistent** — Evan uses "Meeting with SRED.ca", "SR&ED Claim Overview", "SR&ED Conversation", and specific company names interchangeably. The classification logic should rely on attendee emails and organizer, not titles alone.
- **Some meetings are phone-only** — These won't appear in Fireflies. The coach should ask Evan about any calls not captured in the system. C&C was an example of this.
- **Gmail MCP only sees Jude's mailbox** — Cannot directly access Evan's email. HubSpot is the primary source for Evan's email activity (confirmed working: full email bodies, timestamps, recipients, subjects all available via `emails` object type).
- **HubSpot email tracking depends on logging** — If Evan sends an email outside of HubSpot (e.g., directly from Gmail without the HubSpot extension), it may not appear. The coach should ask about any communications not captured in the system.
