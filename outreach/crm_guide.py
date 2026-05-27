# ============================================================
# outreach/crm_guide.md (as Python string for import)
# CRM Stack Recommendations for Bracken & KFEM
# ============================================================

CRM_RECOMMENDATIONS = """
╔══════════════════════════════════════════════════════════════════╗
║  CRM STACK RECOMMENDATIONS — BRACKEN & KFEM DIGITAL SOLUTIONS  ║
╚══════════════════════════════════════════════════════════════════╝

CONTEXT: Nigerian startup, B2B estate market, outbound sales focus,
mobile-heavy team, budget-conscious, WhatsApp-driven communication.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIER 1 — RECOMMENDED (Best fit for your stage)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. PIPEDRIVE (pipedrive.com)
   Cost: ~$15–$25/user/month (Essential/Advanced plan)
   ✅ Best visual pipeline for outbound B2B sales
   ✅ Custom fields for estate leads (score, tier, state, area)
   ✅ CSV import from your scraper exports
   ✅ Mobile app — works well in the field
   ✅ Email integration + call logging
   ✅ Automation for follow-up reminders
   ✅ Good API for future integration with your scraper
   ❌ WhatsApp native integration requires Zapier/Make
   
   VERDICT: Best balance of power + simplicity for a small outbound team.

2. ZOHO CRM (zoho.com/crm)
   Cost: FREE for 3 users | Paid from ~$14/user/month
   ✅ Free tier is genuinely usable for early stage
   ✅ Strong Nigerian user community and support
   ✅ Telephone/WhatsApp integrations via marketplace
   ✅ Bulk CSV import, custom modules
   ✅ Affordable and scalable
   ✅ Built-in email sequences
   ❌ UI can feel cluttered; steeper learning curve
   
   VERDICT: Best value if budget is tight. Free tier handles first 3 reps.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIER 2 — STRONG ALTERNATIVES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. HUBSPOT CRM (hubspot.com)
   Cost: FREE core CRM (unlimited contacts)
   ✅ Completely free CRM — industry-leading
   ✅ Contact/company/deal management
   ✅ Email templates and tracking
   ✅ Seamless CSV import from your scraper
   ✅ Meeting scheduling links
   ❌ Advanced sequences/automation requires paid Sales Hub (~$45/mo)
   ❌ Not optimised for WhatsApp-first workflows
   
   VERDICT: Best free starting point. Upgrade when revenue allows.

4. FRESHSALES (freshworks.com/crm)
   Cost: Free tier | Growth plan ~$15/user/month
   ✅ Clean UI, easy onboarding
   ✅ Built-in phone dialer (with Nigerian number support)
   ✅ Email + WhatsApp integration
   ✅ AI lead scoring (helpful alongside your custom scoring)
   ✅ Pipeline management similar to Pipedrive
   
   VERDICT: Best option if your team makes high call volumes.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIER 3 — WHATSAPP-NATIVE OPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. WATI (wati.io)
   Cost: From ~$49/month (5 agents)
   ✅ Built specifically for WhatsApp Business API
   ✅ Broadcast messages, chatbots, agent routing
   ✅ CRM-lite contact management
   ✅ PERFECT for your WhatsApp outreach sequences
   ❌ Not a full sales CRM — pair with Pipedrive or HubSpot
   
   VERDICT: Use as your WhatsApp layer ON TOP of a full CRM.
   Stack: Pipedrive + WATI = powerful outbound engine.

6. RESPOND.IO (respond.io)
   Cost: From $79/month
   ✅ Multi-channel: WhatsApp + email + SMS + Instagram DM
   ✅ Team inbox for estate lead management
   ✅ CRM integration via Zapier
   
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDED STACK (PHASE 1 — STARTUP)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌──────────────────────────────────────────────────┐
  │  LEAD GENERATION: Your Google Maps Scraper       │
  │         ↓ CSV/Excel export                       │
  │  CRM: Zoho CRM FREE (or HubSpot Free)            │
  │         ↓ Pipeline management                    │
  │  WHATSAPP: WATI or WhatsApp Business App         │
  │         ↓ Broadcast sequences                    │
  │  EMAIL: Gmail / Outlook with Mixmax or Streak    │
  │         ↓ Tracked open rates                     │
  │  CALLING: Skype / Airtel Business number         │
  └──────────────────────────────────────────────────┘
  Monthly cost estimate: ₦15,000–₦50,000 total

RECOMMENDED STACK (PHASE 2 — SCALING):
  ┌──────────────────────────────────────────────────┐
  │  LEAD GENERATION: Scraper (automated, scheduled) │
  │  CRM: Pipedrive (Essential) — $15/user/mo        │
  │  WHATSAPP: WATI Growth — $49/mo                  │
  │  EMAIL: Pipedrive Sequences                      │
  │  AUTOMATION: Zapier (connects everything)        │
  │  ANALYTICS: Google Data Studio (free)            │
  └──────────────────────────────────────────────────┘
  Monthly cost estimate: ₦80,000–₦150,000 total

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CUSTOM FIELDS TO CREATE IN YOUR CRM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For each estate lead, add:
• Estate Name
• State (Lagos / Abuja)
• Area / LGA
• Google Maps URL
• Lead Score (0–100)
• Lead Tier (HOT / WARM / COLD)
• Estate Segment (Luxury / Mid-tier / New / Disorganised)
• Number of Reviews
• Has Website? (Yes/No)
• Has Phone? (Yes/No)
• First Contact Date
• Last Contact Date
• Contact Stage (New / Contacted / Demo Booked / Proposal Sent / Won / Lost)
• Notes
"""
