# Stage-Specific Evaluation Criteria

> The coach must know WHERE Evan is in the sales cycle with each prospect before evaluating his meetings or emails. What's excellent at one stage is wrong at another.

## SRED.ca Sales Pipeline Stages

Mapped from HubSpot pipeline "Sales Pipeline" (Evan's owner ID: 228172981):

| Stage | HubSpot ID | What's Happening | Evan's Primary Job |
|-------|-----------|------------------|-------------------|
| **Opportunity** | `30153821` | Cold/warm prospect identified. No meeting yet. | Get the meeting booked. |
| **SR&ED Assessment** | `appointmentscheduled` | Pitch meeting happened or scheduled. Prospect is being qualified. | Qualify the prospect, explain SR&ED, sell the value, set up technical discovery. |
| **Technical Discovery** | `31821993` | Logan or James meet with the prospect's technical team. | Smooth handoff, clear on contract/pricing, stay engaged without taking over. |
| **Follow-Up** | `contractsent` | Post-discovery. Working toward signed engagement. | Send engagement letter, handle objections, maintain momentum, close. |
| **Closed / Meeting Booked** | `closedwon` | Signed client. | Onboarding support, payment setup, ensure Logan/James have what they need. |
| **Lost or no SR&ED** | `closedlost` | Dead or disqualified. | (Review: what went wrong? Coachable moment?) |

---

## Stage 1: OPPORTUNITY (Getting the Meeting)

**What Evan should be doing:**
- Outbound outreach via email, LinkedIn, and phone
- Personalized messages that reference the prospect's specific situation (trigger events, tech stack, recent funding, etc.)
- Multi-channel cadence: not just email — LinkedIn + email + phone
- Quick response to inbound leads (within 2 hours ideally)

**Email evaluation at this stage:**
- [ ] Is the outreach personalized to THIS company, or is it a template?
- [ ] Does it mention a specific trigger event or reason for reaching out?
- [ ] Is it concise? (Under 150 words — nobody reads long cold emails)
- [ ] Clear CTA: is he asking for a specific meeting time, or vaguely saying "let's chat"?
- [ ] Follow-up cadence: 3-5 touches over 2 weeks, then re-engage after 30 days?
- [ ] Multi-channel: is he pairing email with LinkedIn connection requests?

**Meeting evaluation at this stage:**
- N/A — no meetings yet at this stage. If Evan has a call, it's an intro/qualifying call.
- If there IS a quick intro call: is Evan qualifying (right ICP, has R&D, Canadian payroll) or just pitching?

**Red flags:**
- Sending generic templates to everyone
- Only using one channel (email only, no LinkedIn/phone)
- Giving up after 1-2 touches
- Not responding to inbound leads within 4 hours
- Prospect doesn't match SRED.ca ICP (reference `sred-brand-icp` skill)

---

## Stage 2: SR&ED ASSESSMENT (The Pitch Meeting)

This is Evan's main stage. He leads the call, walks through the deck, explains SR&ED, presents pricing, and qualifies the prospect.

**Meeting evaluation at this stage (full Barrows framework):**

### Before the meeting:
- [ ] Did Evan research the prospect? (Company website, LinkedIn, tech stack, previous SR&ED claims)
- [ ] Did he send a pre-meeting confirmation or agenda?
- [ ] Did he check if the right person will be on the call? (Decision-maker or technical lead)

### During the meeting:
- [ ] **Discovery before pitch:** Did Evan ask about the prospect's business BEFORE jumping into the deck? (What do you do? What does your R&D look like? Have you heard of SR&ED?)
- [ ] **Talk ratio:** Is he in the 50-60% range for a first pitch, or is he monologuing at 70%+?
- [ ] **Qualification questions:** Did he ask about Canadian employees/payroll, fiscal year-end, existing SR&ED claims, other government grants?
- [ ] **Objection handling:** When the prospect pushes back (cost, risk, "we tried this before"), does Evan address it directly or dodge it?
- [ ] **Urgency creation:** Does he explain the 18-month filing deadline? Help them understand the cost of waiting?
- [ ] **Guarantee explanation:** Did he clearly explain the 75% guarantee? (This is SRED.ca's differentiator — it should come up every time)
- [ ] **Pricing clarity:** Was the flat-fee model clearly explained and compared to contingency competitors?
- [ ] **Next steps — PAYMENT FIRST:** Did Evan clearly set the next action as sending the payment link? The payment (Stripe link with LOE baked in) is the GATE to Technical Discovery. No payment = no Logan meeting. This is non-negotiable.
- [ ] **Small talk management:** How long before business starts? (>5 min of hockey talk = flag)

### After the meeting (same-day or next-morning follow-up):
- [ ] **Timeliness:** Follow-up sent within 4 hours of meeting end
- [ ] **Personal touch:** References something specific from the conversation
- [ ] **Value recap:** Restates what SR&ED could mean for THIS specific prospect
- [ ] **Payment link included:** The follow-up email MUST include the Stripe payment link. The LOE (Letter of Engagement) is baked into the payment flow — the prospect signs the LOE as part of making payment. This is the critical conversion step.
- [ ] **Resources attached:** Presentation deck, interview prep guide, example project
- [ ] **Referral follow-through:** If Evan promised an intro (e.g., to Jane for IRAP, to another service), did he include it?
- [ ] **Guarantee mention:** Includes or links to the SR&ED guarantee
- [ ] **Pricing recap:** Restates the fee structure discussed
- [ ] **Info request:** Asks for company name, fiscal year-end, business number, web address
- [ ] **Professional signature:** Proper formatting, booking link, contact info

> **CRITICAL PROCESS RULE:** Payment must happen BEFORE the Technical Discovery meeting with Logan/James is scheduled. The payment link includes the LOE (Letter of Engagement), so getting payment = getting the signed contract. This step serves two purposes: (1) it surfaces objections early — if they won't pay, they're not serious, and (2) it confirms they're qualified and committed before SRED.ca invests Logan/James's time. The coach should ALWAYS check: did Evan collect payment before booking the tech disco?

**Known benchmark — the Sheldrake follow-up (Jan 28, 2026):**
Evan's follow-up to Scott Sheldrake / Numbered GameCo hits nearly every item: coffee invite (personal touch), Jane Ramachandran referral included, interview prep guide attached, guarantee explained with link, pricing stated ($10K startup plan), five specific data points requested, engagement letter referenced, payment link included, and "you have my phone number" as a personal close. This is the bar.

---

## Stage 2→3 GATE: PAYMENT COLLECTION

This is the most important transition in the pipeline. The deal CANNOT move to Technical Discovery until the prospect has paid.

**What needs to happen:**
1. After a positive SR&ED Assessment, Evan sends the Stripe payment link (LOE is baked in)
2. Prospect reviews the LOE, agrees to terms, and makes first payment
3. ONLY THEN does Evan schedule the Technical Discovery meeting with Logan/James

**Coach evaluation:**
- [ ] **Speed to payment link:** How quickly after the Assessment does Evan send the payment link? (Same-day follow-up email with link = ideal)
- [ ] **Payment follow-up cadence:** If the prospect hasn't paid within 3 business days, is Evan following up?
- [ ] **Objection surfacing:** If the prospect pushes back on payment, is Evan handling the objection or just waiting? Common objections: "Can we do the tech meeting first?" (No — payment comes first), "Can you discount?" (Flat fee, no discounting), "I need to talk to my partner" (When? Set a deadline)
- [ ] **Gate enforcement:** Is Evan ever scheduling Logan/James meetings BEFORE payment is received? (This is a red flag — it undermines the process and wastes technical resources)
- [ ] **Deal qualification:** If a prospect won't pay, that's valuable signal. Is Evan marking the deal as lost or letting it sit in limbo?

**Red flags:**
- Tech Discovery scheduled before payment received
- Payment link not sent in the post-Assessment follow-up email
- Prospect has had the payment link for >7 days with no follow-up from Evan
- Evan discounting or offering exceptions to the payment-first process
- Deal sitting between Assessment and Tech Discovery for >14 days with no movement

---

## Stage 3: TECHNICAL DISCOVERY (Logan/James Lead)

**Prerequisite:** Payment has been collected. The LOE is signed. The prospect is now a paying client in the onboarding phase.

Evan takes a back seat here. Logan or James run the technical interview. But Evan still has a job to do.

**Meeting evaluation at this stage:**
- [ ] **Intro clarity:** Does Evan open the call confidently and set the stage for Logan/James?
- [ ] **Contract/pricing recap:** If the prospect asks about pricing or terms, does Evan handle it clearly and confidently? (He should own this — it's not Logan's job)
- [ ] **Handoff quality:** Does the transition from Evan to Logan/James feel smooth, or is there an awkward "uh, I'll pass it to Logan"?
- [ ] **Engagement level:** Does Evan stay present and engaged, or does he check out once Logan starts talking? (He should be noting action items, watching for closing signals)
- [ ] **Administrative items:** Confirms payment was received, explains what happens next (quarterly meetings, technical diary, claim timeline)

**Email evaluation at this stage:**
- [ ] **Pre-meeting prep:** Did Evan send the prospect the interview prep guide and set expectations for the technical meeting? Did he confirm who from the prospect's side should attend (technical lead/CTO)?
- [ ] **Post-meeting follow-up:** Even though Logan leads, Evan should still send a follow-up summarizing next steps and timelines
- [ ] **Internal handoff:** Did Evan brief Logan/James before the call? (Context about the prospect, what was discussed in the pitch, any concerns raised, fiscal year-end, company details)

**Red flags:**
- Evan not on the call at all (he should at least open and close)
- Prospect asks about pricing/terms and Logan has to answer
- No follow-up email after the technical meeting
- Payment not actually received before this meeting happened (process violation)

---

## Stage 4: FOLLOW-UP (Post-Discovery, Active Client)

Technical Discovery is complete. The claim work is underway or being planned. Evan's role shifts to client success and ensuring nothing falls through the cracks.

**Email evaluation at this stage:**
- [ ] **Onboarding confirmation:** Has Evan confirmed the quarterly meeting schedule with the client?
- [ ] **Billing running smoothly:** Are monthly payments coming through without issues? (Reference the Sky High ERP Stripe invoice issue as an example of what can go wrong)
- [ ] **Follow-up cadence:** If no response within 3 business days, is Evan following up?
- [ ] **Objection handling in writing:** If the prospect has concerns (pricing, timing, risk), is Evan addressing them clearly in email?
- [ ] **Urgency reinforcement:** Is he reminding them of the filing deadline or fiscal year-end timing?
- [ ] **Multi-channel:** If email isn't getting responses, is Evan picking up the phone?
- [ ] **Escalation awareness:** If a deal stalls here for >7 days, is Evan flagging it to Jude?

**Red flags:**
- Contract sent but no follow-up for >5 days
- Prospect went quiet and Evan stopped reaching out
- Multiple follow-ups that are just "checking in" with no value-add
- Deal sitting in this stage >30 days without movement

---

## Stage 5: CLOSED / WON (Onboarding)

Client signed. Now it's about smooth onboarding and transition to the delivery team.

**Email evaluation at this stage:**
- [ ] **Welcome/thank you:** Did Evan send a congratulatory email welcoming them as a client?
- [ ] **Onboarding checklist:** Did he clearly communicate next steps (first quarterly meeting, what to prepare, who their project manager is)?
- [ ] **Payment confirmation:** Is the Stripe billing set up correctly and confirmed?
- [ ] **Internal handoff:** Did Evan brief Logan/James with everything from the sales process? (Company background, prospect concerns, key contacts, fiscal year-end, etc.)
- [ ] **Responsiveness:** Is Evan still responsive to client questions, or does he go dark after the close?

**Red flags:**
- Client has to chase Evan for onboarding information
- Logan/James have no context about the client when they start
- Billing/admin issues (like the Sky High ERP Stripe invoice issue) not resolved promptly
- Client CC's Jude because Evan isn't responding

---

## Stage 6: CLOSED / LOST (Post-Mortem)

**Coaching opportunity — every loss is a lesson:**
- Why did it die? (No SR&ED fit? Price objection? Went with a competitor? Just went dark?)
- At what stage did it stall? (The earlier it dies, the more likely it's a qualification issue. Later = closing issue.)
- Was there a pattern? (Third deal lost because Evan didn't follow up? That's a trend.)
- Did Evan ask for feedback from the prospect? (Barrows: "You learn more from the deals you lose")

---

## How the Coach Uses This

Before evaluating ANY meeting or email thread, the coach MUST:

1. **Check the deal stage in HubSpot** for that prospect
2. **Apply the correct evaluation criteria** for that stage
3. **Note where Evan is strong vs. weak at each stage** — patterns across deals at the same stage are more valuable than one-off observations

For example:
- If Evan is great at Stage 2 (pitch) but deals keep dying at Stage 4 (follow-up), the coaching focus should be on closing discipline, not pitch technique.
- If deals at Stage 1 (opportunity) aren't converting to Stage 2 (assessment), the focus should be on outreach quality and cadence.
- If Stage 3 (technical discovery) meetings go well but the contract isn't sent promptly, the focus should be on administrative follow-through.

The weekly brief should include a stage-by-stage snapshot:

```
📊 PIPELINE BY STAGE
--------------------
Opportunity (Stage 1): [X] deals — [list]
SR&ED Assessment (Stage 2): [X] deals — [list]
Technical Discovery (Stage 3): [X] deals — [list]
Follow-Up (Stage 4): [X] deals — [list]
Closed/Won (Stage 5): [X] this week
Closed/Lost (Stage 6): [X] this week

⚠️ STAGE HEALTH FLAGS
- [Deal name] has been in [Stage] for [X] days with no activity
- [Deal name] moved backward from [Stage] to [Stage] — what happened?
- [X] deals in Follow-Up with no email in >5 days
```
