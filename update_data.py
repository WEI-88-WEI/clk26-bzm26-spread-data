#!/usr/bin/env python3
import csv
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://api.hyperliquid.xyz/info"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 clk26-bzm26-spread-data/1.0",
}
COINS = {
    "cl": "xyz:CL",
    "bren": "xyz:BRENTOIL",
}
ROOT = Path(__file__).resolve().parent

OUTPUTS = {
    "1d": {
        "csv": ROOT / "clk26_bzm26_daily_spread.csv",
        "json": ROOT / "data_daily.json",
        "label": "daily",
    },
    "1h": {
        "csv": ROOT / "clk26_bzm26_hourly_spread.csv",
        "json": ROOT / "data_hourly.json",
        "label": "hourly",
    },
}

LEGACY_JSON = ROOT / "data.json"


def post_json(payload: dict):
    req = urllib.request.Request(API_URL, data=json.dumps(payload).encode(), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def bucket_key(ts_ms: int, interval: str):
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    if interval == "1d":
        return dt.strftime("%Y-%m-%d")
    if interval == "1h":
        return dt.strftime("%Y-%m-%d %H:00")
    raise ValueError(f"Unsupported interval: {interval}")


def fetch_candles(coin: str, interval: str):
    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": coin,
            "interval": interval,
            "startTime": 0,
            "endTime": int(datetime.now(tz=timezone.utc).timestamp() * 1000),
        },
    }
    candles = post_json(payload)
    out = {}
    for c in candles:
        key = bucket_key(c["t"], interval)
        out[key] = {
            "bucket": key,
            "symbol": c["s"],
            "open": float(c["o"]),
            "high": float(c["h"]),
            "low": float(c["l"]),
            "close": float(c["c"]),
            "volume": float(c["v"]),
            "trades": int(c["n"]),
            "start_time": c["t"],
            "end_time": c["T"],
        }
    return out


def build_spread_rows(cl_map, bren_map):
    keys = sorted(set(cl_map.keys()) & set(bren_map.keys()))
    rows = []
    for key in keys:
        cl = cl_map[key]
        bren = bren_map[key]
        spread_abs = bren["close"] - cl["close"]
        spread_pct = (spread_abs / cl["close"]) if cl["close"] else None
        rows.append({
            "bucket": key,
            "cl_open": cl["open"],
            "cl_high": cl["high"],
            "cl_low": cl["low"],
            "cl_close": cl["close"],
            "bren_open": bren["open"],
            "bren_high": bren["high"],
            "bren_low": bren["low"],
            "bren_close": bren["close"],
            "spread_abs_bren_minus_cl": spread_abs,
            "spread_pct_vs_cl": spread_pct,
        })
    return rows


def write_csv(path: Path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "bucket",
                "cl_open", "cl_high", "cl_low", "cl_close",
                "bren_open", "bren_high", "bren_low", "bren_close",
                "spread_abs_bren_minus_cl",
                "spread_pct_vs_cl",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({
                k: (f"{row[k]:.6f}" if isinstance(row[k], float) else row[k])
                for k in row
            })


def write_json(path: Path, interval: str, rows, cl_map, bren_map):
    payload = {
        "meta": {
            "source": "Hyperliquid Info API",
            "dex": "xyz",
            "interval": interval,
            "updated_at": datetime.now(tz=timezone.utc).isoformat(),
            "symbols": {
                "cl": COINS["cl"],
                "bren": COINS["bren"],
            },
            "counts": {
                "cl_bars": len(cl_map),
                "bren_bars": len(bren_map),
                "overlap_bars": len(rows),
            },
        },
        "series": {
            "buckets": [r["bucket"] for r in rows],
            "cl_close": [r["cl_close"] for r in rows],
            "bren_close": [r["bren_close"] for r in rows],
            "spread_abs_bren_minus_cl": [r["spread_abs_bren_minus_cl"] for r in rows],
            "spread_pct_vs_cl": [r["spread_pct_vs_cl"] for r in rows],
        },
        "rows": rows,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generate(interval: str):
    cl_map = fetch_candles(COINS["cl"], interval)
    bren_map = fetch_candles(COINS["bren"], interval)
    rows = build_spread_rows(cl_map, bren_map)
    write_csv(OUTPUTS[interval]["csv"], rows)
    write_json(OUTPUTS[interval]["json"], interval, rows, cl_map, bren_map)
    return {
        "interval": interval,
        "cl_bars": len(cl_map),
        "bren_bars": len(bren_map),
        "overlap_bars": len(rows),
        "first_overlap": rows[0]["bucket"] if rows else None,
        "last_overlap": rows[-1]["bucket"] if rows else None,
    }


def main():
    daily = generate("1d")
    hourly = generate("1h")
    LEGACY_JSON.write_text((ROOT / "data_hourly.json").read_text(encoding="utf-8"), encoding="utf-8")
    print(json.dumps({"daily": daily, "hourly": hourly}, ensure_ascii=False))


if __name__ == "__main__":
    main()
