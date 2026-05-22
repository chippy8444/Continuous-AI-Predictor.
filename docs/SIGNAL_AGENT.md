# RA Signal Agent

This agent collects public, source-bounded signals for the Continuous AI / Resolution Assurance repository.

It was built from the supplied systemic signal framework covering banking/CRE, food, water, critical minerals, institutional trust, supply-chain disruption, and civil-unrest proxy signals.

## What it does

- Runs on GitHub Actions every 6 hours, or manually with `workflow_dispatch`.
- Reads `signal_sources.yml`.
- Fetches each source as CSV, text-watch, or GDELT timeline.
- Stores a small observation record instead of storing whole webpages.
- Writes `data/raw/YYYY-MM-DD/<signal_id>.json`, `data/signals/YYYY-MM-DD.jsonl`, `data/latest.json`, `data/metrics.csv`, and `reports/latest.md`.
- Commits generated data back to the repo.
- Treats source failures as `negative_space`, not as missing data to ignore.

## What it does not do

- It does not claim a collapse date.
- It does not provide financial, legal, medical, emergency, or investment advice.
- It does not treat media volume as truth.
- It does not store full scraped content.
- It does not guarantee that any public source is complete, current, or unbiased.

## Agent states

| State | Meaning |
|---|---|
| `monitor` | Signal present but below configured thresholds |
| `watch` | Signal crossed early threshold |
| `alert` | Signal crossed escalation threshold |
| `critical` | Signal crossed critical threshold |
| `negative_space` | Source was missing, unreachable, or unparsable |

## Signal domains

| Domain | Purpose |
|---|---|
| `banking_cre` | CRE, credit, bank stress, and stress-test watch |
| `food` | food price, shortage, fertilizer, and commodity pressure |
| `water` | drought, groundwater, reservoir/rationing watch |
| `critical_minerals` | lithium/copper/critical mineral bottleneck watch |
| `institutional_trust` | trust, legitimacy, and polarization watch |
| `supply_chain` | shipping, ports, logistics, and bottleneck watch |
| `civil_unrest` | protest, riot, and unrest proxy watch |

## How to run locally

```bash
python -m pip install -r requirements.txt
python signal_agent.py
```

## How to add a new signal

Add a new item under `sources:` in `signal_sources.yml`.

### CSV source

```yaml
- id: example_csv_signal
  name: Example CSV Signal
  domain: food
  type: csv
  url: https://example.com/data.csv
  date_column: observation_date
  value_column: VALUE
  unit: index
  direction: high_bad
  thresholds:
    warning: 10
    alert: 20
    critical: 30
```

### Text watch source

```yaml
- id: example_text_watch
  name: Example Text Watch
  domain: water
  type: text_watch
  url: https://example.com/report
  keywords:
    - drought
    - rationing
    - aquifer
  thresholds:
    warning_hits: 1
    alert_hits: 3
    critical_hits: 7
```

### GDELT source

```yaml
- id: example_gdelt_watch
  name: Example GDELT Watch
  domain: civil_unrest
  type: gdelt_timeline
  query: '("civil unrest" OR protest OR riot)'
  timespan: 7d
  thresholds:
    warning: 0.5
    alert: 1.5
    critical: 3.0
```

## Canon-safe interpretation

The output is an evidence ledger. It can support later RA analysis, but the raw collector itself only says:

> This source was checked at this time, this value/text signal was observed, this digest was recorded, and this threshold state was assigned.

That makes the collector safer to publish as monitoring infrastructure while keeping stronger claims separated into an audited interpretation layer.
