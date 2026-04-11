# Numbers Protocol Audit Agent

An AI agent that verifies the provenance of China Times (中時) assets on the Numbers Protocol x402 standard, recording every verification as an immutable on-chain commit on Numbers Mainnet.

## What it does

1. **Fetches** all assets from the China Times x402 showcase page
2. **Verifies** each asset's metadata against the Numbers Protocol DIA Backend API
3. **Commits** each verification result on-chain via Numbers Mainnet
4. **Logs** a full audit trail locally and on-chain

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo>
cd numbers-audit-agent
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:

- `CAPTURE_TOKEN` — your Numbers Protocol Capture API token
- `CAPTURE_WALLET` — your wallet address
- `AGENT_NID` — (optional) pre-registered agent identity Nid

### 3. Run the agent

```bash
python main.py
```

If `AGENT_NID` is not set, the agent will prompt you for an image to register as its on-chain identity.

## Project Structure

```
numbers-audit-agent/
├── .env                  # Your credentials (never commit this)
├── .env.example          # Template
├── requirements.txt      # Dependencies
├── main.py               # Entry point
├── config/
│   └── settings.py       # Loads environment variables
├── agent/
│   ├── fetcher.py        # Fetches assets from China Times API
│   ├── verifier.py       # Cross-references DIA Backend metadata
│   ├── committer.py      # Writes on-chain commits via Capture API
│   └── reporter.py       # Terminal UI and logging
└── logs/                 # Local audit logs (auto-generated)
```

## On-chain Activity

Each run produces:

- One agent identity registration (first run only)
- One on-chain commit per verified asset containing:
  - Asset Nid audited
  - Verification status
  - Timestamp
  - Agent identity reference

All activity is permanently recorded on Numbers Mainnet and queryable via the Numbers Protocol explorer.
