# Numbers Protocol Audit Agent

An AI agent that verifies the provenance of China Times (中時新聞網) digital assets registered on the Numbers Protocol x402 standard. Each verification is recorded as an immutable on-chain commit on Numbers Mainnet, creating a permanent, auditable history of the agent's activity.

---

## What It Does

1. **Fetches** all assets from the China Times x402 showcase page via the PyroImage API
2. **Verifies** each asset's provenance by cross-referencing the Numbers Protocol DIA Backend API across 6 checks
3. **Commits** each verification result on-chain to the agent's own asset history on Numbers Mainnet
4. **Logs** a full audit trail locally and on-chain

---

## Verification Checks

For each asset, the agent runs the following checks against the DIA Backend:

| Check                  | Description                                                 |
| ---------------------- | ----------------------------------------------------------- |
| `nid_match`            | Asset Nid matches between the showcase page and DIA Backend |
| `published_and_public` | Asset is published and publicly accessible                  |
| `on_chain_integrity`   | Asset has at least one integrity record on Numbers Mainnet  |
| `title_match`          | Asset headline matches between both sources                 |
| `creator_verified`     | Creator belongs to a known 中時新聞網 alias                 |
| `timestamp_match`      | Upload timestamp matches between both sources               |

**Status outcomes:**

- `VERIFIED` — all 6 checks passed
- `MISMATCH` — asset found but one or more checks failed
- `FAILED` — asset not found in DIA Backend

---

## On-Chain Architecture

All commits are anchored to the **agent's own registered asset Nid**, not the individual China Times assets. This means the agent's entire verification history accumulates in one place — queryable like a Git log by looking up the agent's Nid on the Numbers Mainnet explorer.

```
Agent Asset (your Nid)
  └── Commit: audited "WBCQ TPE VS ESP"        → VERIFIED
  └── Commit: audited "Mengjia Longshan Temple" → VERIFIED
  └── Commit: audited "NVIDIA CEO Jensen Huang" → VERIFIED
  ... 48 commits total
```

Each commit's `custom` payload contains the full verification result including the audited asset's Nid, title, status, checks passed, and any mismatches.

---

## Project Structure

```
numbers-audit-agent/
├── .env                  # Your credentials (never commit this)
├── .env.example          # Template — copy to .env and fill in
├── .gitignore
├── requirements.txt
├── main.py               # Entry point — orchestrates all steps
├── config/
│   └── settings.py       # Loads and validates environment variables
├── agent/
│   ├── fetcher.py        # Fetches assets from PyroImage API + DIA Backend
│   ├── verifier.py       # Cross-references and runs 6 provenance checks
│   ├── committer.py      # Registers agent identity + writes on-chain commits
│   └── reporter.py       # Interactive terminal UI and local logging
└── logs/                 # Auto-generated audit logs per run
```

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/YOUR_USERNAME/numbers-audit-agent.git
cd numbers-audit-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
CAPTURE_TOKEN=your_capture_token_here
CAPTURE_WALLET=your_wallet_address_here
AGENT_NID=                        # Leave blank on first run
AGENT_NAME=Numbers Audit Agent    # Will be prompted on first run
```

Your Capture token can be obtained from the [Capture app](https://captureapp.xyz).

### 3. Run a dry run first

```bash
python main.py --dry-run
```

This runs the full verification sweep without writing any on-chain commits. Use this to confirm everything is working before going live.

### 4. Run the full agent

```bash
python main.py
```

---

## First Run — Agent Identity Registration

If `AGENT_NID` is not set in your `.env`, the agent will guide you through a one-time setup:

```
Let's set up your agent's on-chain identity.

Enter a name for your agent: My Audit Agent
Enter path to agent image (PNG/JPG): /path/to/your/image.png

⛓  Checking if image is already registered on Numbers Mainnet...
✅ Agent "My Audit Agent" registered on Numbers Mainnet!

Important: Add these to your .env to skip setup next time:
AGENT_NID=bafybei...
AGENT_NAME=My Audit Agent
```

**Smart registration:** The agent computes the SHA-256 hash of your image and checks if it's already registered on your Capture account before registering a new one. If it finds an existing registration it reuses that Nid at no cost.

Registration costs 0.1 NUM + gas from your Capture account. Subsequent runs are free.

---

## Usage

```bash
# Dry run — verification only, no on-chain commits
python main.py --dry-run

# Full run — verification + on-chain commits
python main.py
```

---

## Viewing On-Chain Activity

After a live run, look up your agent's Nid on the Numbers Mainnet explorer to see its full commit history:

```
https://mainnet.num.network/address/YOUR_AGENT_NID
```

---

## Environment Variables

| Variable          | Required | Description                                         |
| ----------------- | -------- | --------------------------------------------------- |
| `CAPTURE_TOKEN`   | ✅       | Your Numbers Protocol Capture API token             |
| `CAPTURE_WALLET`  | ✅       | Your Capture wallet address                         |
| `AGENT_NID`       | ⬜       | Agent's registered Nid (set after first run)        |
| `AGENT_NAME`      | ⬜       | Agent's display name (default: Numbers Audit Agent) |
| `PYRO_API_URL`    | ⬜       | PyroImage API endpoint (default provided)           |
| `PYRO_ORG_ID`     | ⬜       | China Times org ID (default provided)               |
| `DIA_BACKEND_URL` | ⬜       | Numbers Protocol DIA Backend URL (default provided) |
| `COMMIT_API_URL`  | ⬜       | Numbers Mainnet commit endpoint (default provided)  |

---

## Local Logs

Each run generates a timestamped log file in the `logs/` directory:

```
logs/audit_20260411_100347.log
```

Logs contain the full verification result for every asset including Nid, status, checks passed, mismatches, and commit transaction hashes.
