# Bracken & KFEM Digital Solutions
## Estate Lead Scraper — Production Grade

> Google Maps estate intelligence system for cold outreach across Nigerian gated estates.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Quick Start — Windows (Local)](#quick-start--windows-local)
4. [Configuration](#configuration)
5. [Running the Scraper](#running-the-scraper)
6. [Lead Scoring System](#lead-scoring-system)
7. [Output Files](#output-files)
8. [Outreach Scripts](#outreach-scripts)
9. [Azure VM Deployment](#azure-vm-deployment)
10. [Scaling to All Nigerian States](#scaling-to-all-nigerian-states)
11. [Legal & Ethical Notes](#legal--ethical-notes)
12. [CRM Integration](#crm-integration)

---

## Project Overview

This system scrapes Google Maps for every gated estate, residential community,
property management company, and homeowners association in Lagos and Abuja —
then scores and ranks them as B2B leads for Bracken & KFEM's cold outreach.

**What it produces:**
- Excel workbook with HOT / WARM / COLD lead tiers, color-coded
- CSV for CRM import
- Raw JSON for reprocessing
- Full logging for audit and debug

---

## Project Structure

```
bracken_kfem_scraper/
├── main.py                    ← CLI entry point
├── requirements.txt
├── .env.example               ← Copy to .env and fill in
├── config/
│   ├── settings.py            ← All config, reads .env
│   └── keywords.py            ← Search queries (Lagos + Abuja)
├── scraper/
│   ├── core/
│   │   ├── browser.py         ← Playwright browser manager
│   │   ├── maps_scraper.py    ← Google Maps search + detail scraper
│   │   ├── orchestrator.py    ← Main pipeline coordinator
│   │   └── models.py          ← Pydantic data models
│   ├── utils/
│   │   ├── logger.py          ← Loguru structured logging
│   │   ├── user_agents.py     ← Rotating user agents
│   │   ├── proxy_manager.py   ← Proxy pool management
│   │   ├── deduplicator.py    ← Cross-session deduplication
│   │   └── progress_tracker.py ← Resume-on-crash support
│   └── exporters/
│       └── exporter.py        ← CSV + Excel export
├── leads/
│   └── scorer.py              ← Lead scoring engine (0–100)
├── outreach/
│   ├── scripts.py             ← All cold call / WhatsApp / email scripts
│   └── crm_guide.py           ← CRM stack recommendations
├── data/
│   ├── raw/                   ← Raw JSON checkpoints
│   ├── cleaned/               ← Cleaned data
│   └── exports/               ← Final CSV + Excel outputs
├── screenshots/               ← Auto-captured on errors
└── logs/                      ← Rotating log files
```

---

## Quick Start — Windows (Local)

### Step 1: Prerequisites
- Python 3.11+ (download from python.org)
- Git (optional, for cloning)
- Windows 10/11 or Windows Server 2022

### Step 2: Create Virtual Environment

```batch
cd bracken_kfem_scraper

:: Create venv
python -m venv venv

:: Activate it
venv\Scripts\activate

:: You should now see (venv) in your prompt
```

### Step 3: Install Dependencies

```batch
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install Playwright Browsers

```batch
:: Install Chromium (required)
playwright install chromium

:: Install all browsers (optional)
playwright install

:: Install system dependencies (if needed on Windows)
playwright install-deps
```

### Step 5: Configure Environment

```batch
:: Copy the example .env file
copy .env.example .env

:: Open in Notepad and review settings
notepad .env
```

Key settings to review in `.env`:
- `SCRAPER_HEADLESS=false` — set to `false` first to see the browser
- `SCRAPER_DELAY_MIN` / `SCRAPER_DELAY_MAX` — rate limiting between requests
- `SCRAPER_CONCURRENT_TABS=2` — keep at 2 to avoid detection

---

## Running the Scraper

### Run full scrape (Lagos + Abuja)
```batch
python main.py scrape
```

### Run for a single state
```batch
python main.py scrape --states lagos
python main.py scrape --states abuja
```

### Resume an interrupted session
```batch
python main.py scrape --session-id 20240601_143022
```

### Fresh start (ignore previous progress)
```batch
python main.py scrape --no-resume --session-id my_fresh_run
```

### Re-score existing data (no re-scraping)
```batch
python main.py rescore data/raw/raw_20240601_143022.json
```

### View latest stats
```batch
python main.py stats
```

---

## Configuration

All settings are in `.env`. Key parameters:

| Setting | Default | Description |
|---|---|---|
| `SCRAPER_HEADLESS` | `true` | Run browser headlessly (false to watch) |
| `SCRAPER_DELAY_MIN` | `2.5` | Min seconds between requests |
| `SCRAPER_DELAY_MAX` | `6.0` | Max seconds between requests |
| `SCRAPER_CONCURRENT_TABS` | `2` | Parallel browser tabs (keep low) |
| `SCRAPER_MAX_RESULTS_PER_SEARCH` | `120` | Results per query |
| `SCRAPER_BATCH_SIZE` | `50` | Queries per batch before checkpoint |
| `PROXY_ENABLED` | `false` | Enable proxy rotation |

---

## Lead Scoring System

Each scraped record is scored 0–100 based on:

| Factor | Weight | Logic |
|---|---|---|
| Review count | 25% | More reviews = larger, established estate |
| Rating | 15% | Higher rating = professionally managed |
| No website | 20% | **Opportunity bonus** — they need digital infra |
| Luxury keywords | 25% | Ikoyi, VI, Maitama, premium, luxury, etc. |
| Has phone | 15% | Contactable = reachable lead |

**Tiers:**
- 🔥 **HOT** (70–100): Priority outreach, personal call + WhatsApp
- 🟡 **WARM** (40–69): Email + WhatsApp sequence
- 🔵 **COLD** (0–39): Email only, monthly follow-up

---

## Output Files

All exports land in `data/exports/`:

```
bracken_all_leads_20240601_143022.csv     ← CRM import ready
bracken_all_leads_20240601_143022.xlsx    ← 4 sheets: Dashboard, HOT, WARM, All
data/raw/raw_final_20240601_143022.json   ← Full raw data for reprocessing
```

The Excel workbook contains:
1. **📊 Dashboard** — Summary stats and counts
2. **🔥 HOT Prospects** — Priority outreach list
3. **🟡 WARM Prospects** — Secondary pipeline
4. **All Leads** — Every record, color-coded by tier

---

## Outreach Scripts

All scripts are in `outreach/scripts.py`.

To print all scripts:
```python
from outreach.scripts import print_all_scripts
print_all_scripts()
```

Available scripts:
- `cold_call_luxury` — Script for Ikoyi/VI/Maitama estates
- `cold_call_mid_tier` — Standard residential estates
- `cold_call_disorganized` — Pain-point focused opening
- `whatsapp_luxury` — 3-message WhatsApp sequence (luxury)
- `whatsapp_mid_tier` — 2-message WhatsApp sequence
- `email_luxury` — Full email for premium estates
- `email_mid_tier` — Concise email for mid-tier
- `follow_up_cadence` — Full cadence guide (HOT/WARM/COLD)
- `dm_estate_manager` — LinkedIn/Instagram DM

---

## Azure VM Deployment

### Step 1: Create Azure VM

```bash
# Recommended: Ubuntu 22.04 LTS, Standard_B2s (2 vCPU, 4GB RAM)
# Minimum: 2 vCPU, 4GB RAM
# Recommended: 4 vCPU, 8GB RAM for concurrent scraping
```

In Azure Portal or CLI:
```bash
az vm create \
  --resource-group bracken-rg \
  --name bracken-scraper-vm \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --admin-username azureuser \
  --generate-ssh-keys
```

### Step 2: Connect to VM

```bash
ssh azureuser@<YOUR_VM_IP>
```

### Step 3: Install System Dependencies

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Playwright system dependencies
sudo apt install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
  libxrandr2 libgbm1 libasound2
```

### Step 4: Upload and Configure Project

```bash
# Option A: Git
git clone https://github.com/your-org/bracken-scraper.git
cd bracken-scraper

# Option B: SCP from Windows
# scp -r C:\bracken_kfem_scraper azureuser@<VM_IP>:~/

# Create venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Playwright browsers (headless)
playwright install chromium
playwright install-deps chromium

# Configure environment
cp .env.example .env
nano .env  # Set SCRAPER_HEADLESS=true
```

### Step 5: Run as Background Service

```bash
# Option A: nohup (simple)
nohup python main.py scrape > logs/scrape.log 2>&1 &
echo "PID: $!"

# Option B: screen (recommended for long runs)
sudo apt install screen
screen -S bracken-scraper
source venv/bin/activate
python main.py scrape
# Detach: Ctrl+A then D
# Reattach: screen -r bracken-scraper

# Option C: systemd service (production)
sudo nano /etc/systemd/system/bracken-scraper.service
```

Systemd service file:
```ini
[Unit]
Description=Bracken KFEM Estate Scraper
After=network.target

[Service]
Type=simple
User=azureuser
WorkingDirectory=/home/azureuser/bracken_kfem_scraper
Environment="PATH=/home/azureuser/bracken_kfem_scraper/venv/bin"
ExecStart=/home/azureuser/bracken_kfem_scraper/venv/bin/python main.py scrape
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable bracken-scraper
sudo systemctl start bracken-scraper
sudo journalctl -u bracken-scraper -f  # Watch logs
```

### Step 6: Download Results

```bash
# From your local Windows machine:
scp azureuser@<VM_IP>:~/bracken_kfem_scraper/data/exports/*.xlsx C:\Downloads\
scp azureuser@<VM_IP>:~/bracken_kfem_scraper/data/exports/*.csv C:\Downloads\
```

---

## Scaling to All Nigerian States

To add more states (e.g., Port Harcourt, Kano, Enugu):

1. Open `config/keywords.py`
2. Add a new areas list:
```python
PORT_HARCOURT_AREAS = [
    "GRA", "Trans Amadi", "Old GRA", "Peter Odili Road",
    "Rumuola", "Rumuigbo", "Eliozu", "Rukpokwu", ...
]
```
3. Add to `generate_all_search_queries`:
```python
elif state.lower() in ["port harcourt", "rivers"]:
    areas = PORT_HARCOURT_AREAS
```
4. Run:
```batch
python main.py scrape --states "Port Harcourt"
```

---

## Legal & Ethical Notes

This tool is built for **business intelligence and internal lead generation**.

- Rate limiting (2–6 second delays) is built in — do not reduce below 2 seconds
- Concurrent tabs are capped at 2 by default
- This is not a bulk data redistribution tool — data is for internal CRM use
- Google Maps Terms of Service prohibit bulk scraping for commercial redistribution;
  use this tool for internal sales intelligence only
- Review Google's ToS periodically: https://maps.google.com/help/terms_maps/
- Consider using the Google Places API for higher-volume, ToS-compliant access
  (pricing: ~$0.017 per request after free tier)

---

## CRM Integration

See `outreach/crm_guide.py` for full CRM stack recommendations.

**Quick recommendation:** Start with **Zoho CRM Free** or **HubSpot Free**,
import your Excel exports, and pair with **WATI** for WhatsApp outreach.

---

*Built for Bracken & KFEM Digital Solutions. Internal use only.*
