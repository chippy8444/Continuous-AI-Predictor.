#!/usr/bin/env python3
import csv, datetime as dt, hashlib, html, io, json, os, re, time
from pathlib import Path
from urllib.parse import urlencode

import requests, yaml

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "signal_sources.yml"
DATA = ROOT / "data"
RAW = DATA / "raw"
SIGNALS = DATA / "signals"
REPORTS = ROOT / "reports"
RUN_ID = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
TODAY = dt.datetime.now(dt.timezone.utc).date().isoformat()
UA = os.getenv("RA_SIGNAL_AGENT_USER_AGENT", "RA-Signal-Agent/1.0")

def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def clean_html(x):
    x = re.sub(r"(?is)<script.*?</script>|<style.*?</style>", " ", x)
    x = re.sub(r"(?s)<[^>]+>", " ", x)
    return re.sub(r"\s+", " ", html.unescape(x)).strip()

def digest(x):
    return hashlib.sha256(x.encode("utf-8", "replace")).hexdigest()

def fnum(x):
    if x is None: return None
    try: return float(str(x).strip().replace(",", "").replace("%", ""))
    except Exception: return None

def score_num(v, thresholds, direction="high_bad"):
    if v is None: return 0, "monitor"
    def cross(k):
        t = fnum(thresholds.get(k))
        if t is None: return False
        return v >= t if direction == "high_bad" else v <= t
    if cross("critical"): return 90, "critical"
    if cross("alert"): return 70, "alert"
    if cross("warning"): return 45, "watch"
    return 10, "monitor"

def score_hits(hits, thresholds):
    if hits >= int(thresholds.get("critical_hits", 7)): return 85, "critical"
    if hits >= int(thresholds.get("alert_hits", 3)): return 65, "alert"
    if hits >= int(thresholds.get("warning_hits", 1)): return 35, "watch"
    return 5, "monitor"

def fetch(url):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    return r.text

def base_obs(src):
    return {
        "run_id": RUN_ID, "collected_at": now(),
        "signal_id": src["id"], "domain": src["domain"],
        "source_name": src["name"], "source_type": src["type"],
        "source_url": src.get("url") or src.get("query", ""),
        "status": "ok", "value": None, "value_text": None, "value_date": None,
        "unit": src.get("unit"), "severity": 0, "state": "monitor",
        "confidence": 0.0, "trend": None, "trend_window": None,
        "keyword_hits": None, "source_digest": None,
        "evidence_excerpt": None, "negative_space": False, "error": None,
    }

def fail(src, err):
    o = base_obs(src)
    o.update({
        "status": "error", "state": "negative_space", "severity": 25,
        "confidence": 0.05, "negative_space": True,
        "error": str(err)[:500],
        "evidence_excerpt": "Source unavailable/unparsable; recorded as negative space.",
    })
    return o

def collect_csv(src):
    text = fetch(src["url"])
    rows = list(csv.DictReader(io.StringIO(text)))
    date_col = src.get("date_column", "observation_date")
    val_col = src.get("value_column")
    series = []
    for row in rows:
        v = fnum(row.get(val_col))
        if v is not None:
            series.append((row.get(date_col), v))
    if not series:
        raise RuntimeError("no numeric rows found")
    d, v = series[-1]
    o = base_obs(src)
    sev, state = score_num(v, src.get("thresholds", {}), src.get("direction", "high_bad"))
    trend_window = int(src.get("trend_window", 4))
    trend = None
    if len(series) > trend_window:
        trend = round(v - series[-1 - trend_window][1], 6)
    o.update({
        "value": v, "value_date": d, "severity": sev, "state": state,
        "confidence": 0.9, "trend": trend, "trend_window": trend_window,
        "source_digest": digest(text),
        "evidence_excerpt": f"{val_col}={v} at {date_col}={d}",
    })
    return o

def collect_text(src):
    text = fetch(src["url"])
    plain = clean_html(text)
    hits = sum(plain.lower().count(k.lower()) for k in src.get("keywords", []))
    sev, state = score_hits(hits, src.get("thresholds", {}))
    excerpt = plain[:260]
    for k in src.get("keywords", []):
        p = plain.lower().find(k.lower())
        if p >= 0:
            excerpt = plain[max(0, p-80):p+180]
            break
    o = base_obs(src)
    o.update({
        "value_text": f"{hits} keyword hits", "unit": "keyword_hits",
        "severity": sev, "state": state, "confidence": 0.5,
        "keyword_hits": hits, "source_digest": digest(text),
        "evidence_excerpt": excerpt,
    })
    return o

def collect_gdelt(src):
    params = {
        "query": src["query"], "mode": "timelinevolinfo",
        "format": "json", "timespan": src.get("timespan", "7d")
    }
    url = "https://api.gdeltproject.org/api/v2/doc/doc?" + urlencode(params)
    text = fetch(url)
    payload = json.loads(text)
    timeline = payload.get("timeline") or payload.get("timelinevol") or []
    v, d = None, None
    if isinstance(timeline, list) and timeline:
        last = timeline[-1]
        if isinstance(last, dict):
            v = fnum(last.get("value") or last.get("norm") or last.get("Volume Intensity"))
            d = str(last.get("date") or last.get("datetime") or "")
    if v is None:
        v = float(len(text))
    sev, state = score_num(v, src.get("thresholds", {}), src.get("direction", "high_bad"))
    o = base_obs(src)
    o.update({
        "source_url": url, "value": v, "value_date": d,
        "severity": sev, "state": state, "confidence": 0.75,
        "source_digest": digest(text),
        "evidence_excerpt": f"GDELT query={src['query']} timespan={params['timespan']}",
    })
    return o

COLLECTORS = {"csv": collect_csv, "text_watch": collect_text, "gdelt_timeline": collect_gdelt}

def write_outputs(observations):
    (RAW / TODAY).mkdir(parents=True, exist_ok=True)
    SIGNALS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    for o in observations:
        (RAW / TODAY / f"{o['signal_id']}.json").write_text(json.dumps(o, indent=2), encoding="utf-8")

    with open(SIGNALS / f"{TODAY}.jsonl", "a", encoding="utf-8") as f:
        for o in observations:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

    csv_path = DATA / "metrics.csv"
    fields = ["run_id","collected_at","signal_id","domain","source_name","source_type","status","value","value_date","unit","severity","state","confidence","trend","trend_window","keyword_hits","negative_space","source_url","error"]
    exists = csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields)
        if not exists: w.writeheader()
        for o in observations: w.writerow({k: o.get(k) for k in fields})

    domains = {}
    for o in observations:
        b = domains.setdefault(o["domain"], {"domain": o["domain"], "sources": 0, "ok": 0, "negative_space": 0, "max_severity": 0, "states": {}})
        b["sources"] += 1
        b["ok"] += o["status"] == "ok"
        b["negative_space"] += bool(o["negative_space"])
        b["max_severity"] = max(b["max_severity"], o["severity"])
        b["states"][o["state"]] = b["states"].get(o["state"], 0) + 1

    max_sev = max([o["severity"] for o in observations], default=0)
    global_state = "critical" if max_sev >= 85 else "alert" if max_sev >= 65 else "watch" if max_sev >= 35 else "monitor"
    latest = {
        "run_id": RUN_ID, "generated_at": now(), "global_state": global_state,
        "global_severity": max_sev, "source_count": len(observations),
        "ok_count": sum(o["status"] == "ok" for o in observations),
        "negative_space_count": sum(bool(o["negative_space"]) for o in observations),
        "triangulation": list(domains.values()),
        "notes": [
            "Source-bounded signal ledger, not a certainty engine.",
            "Negative space means source failed/missing/stale, not proof of absence.",
            "Forecast states are monitoring labels only, not advice."
        ],
        "latest_observations": observations,
    }
    (DATA / "latest.json").write_text(json.dumps(latest, indent=2), encoding="utf-8")

    lines = [f"# RA Signal Agent Report — {TODAY}", "", f"**Global state:** `{global_state}`  ", f"**Global severity:** {max_sev}/100", "", "| Domain | Sources | OK | Negative space | Max severity |", "|---|---:|---:|---:|---:|"]
    for d in latest["triangulation"]:
        lines.append(f"| {d['domain']} | {d['sources']} | {d['ok']} | {d['negative_space']} | {d['max_severity']} |")
    lines += ["", "## Observations", "", "| Signal | Domain | Status | State | Severity | Evidence |", "|---|---|---|---|---:|---|"]
    for o in observations:
        ev = (o.get("evidence_excerpt") or o.get("error") or "").replace("|", "\\|")[:180]
        lines.append(f"| `{o['signal_id']}` | {o['domain']} | {o['status']} | {o['state']} | {o['severity']} | {ev} |")
    (REPORTS / "latest.md").write_text("\n".join(lines), encoding="utf-8")

def main():
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    observations = []
    for src in cfg.get("sources", []):
        if src.get("enabled", True) is False:
            continue
        try:
            obs = COLLECTORS[src["type"]](src)
        except Exception as e:
            obs = fail(src, e)
        observations.append(obs)
        time.sleep(float(cfg.get("request_delay_seconds", 0.5)))
    write_outputs(observations)
    print(json.dumps({"run_id": RUN_ID, "sources": len(observations), "ok": sum(o["status"]=="ok" for o in observations)}, indent=2))

if __name__ == "__main__":
    main()
