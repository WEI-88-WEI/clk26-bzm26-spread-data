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
CSV_PATH = ROOT / "clk26_bzm26_daily_spread.csv"
JSON_PATH = ROOT / "data.json"


def post_json(payload: dict):
    req = urllib.request.Request(API_URL, data=json.dumps(payload).encode(), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def fetch_daily_candles(coin: str):
    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": coin,
            "interval": "1d",
            "startTime": 0,
            "endTime": int(datetime.now(tz=timezone.utc).timestamp() * 1000),
        },
    }
    candles = post_json(payload)
    out = {}
    for c in candles:
        day = datetime.fromtimestamp(c["t"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
        out[day] = {
            "date": day,
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
    dates = sorted(set(cl_map.keys()) & set(bren_map.keys()))
    rows = []
    for d in dates:
        cl = cl_map[d]
        bren = bren_map[d]
        spread_abs = bren["close"] - cl["close"]
        spread_pct = (spread_abs / cl["close"]) if cl["close"] else None
        rows.append({
            "date": d,
            "cl_close": cl["close"],
            "bren_close": bren["close"],
            "spread_abs_bren_minus_cl": spread_abs,
            "spread_pct_vs_cl": spread_pct,
        })
    return rows


def write_csv(rows):
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date",
                "cl_close",
                "bren_close",
                "spread_abs_bren_minus_cl",
                "spread_pct_vs_cl",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "date": row["date"],
                "cl_close": f"{row['cl_close']:.6f}",
                "bren_close": f"{row['bren_close']:.6f}",
                "spread_abs_bren_minus_cl": f"{row['spread_abs_bren_minus_cl']:.6f}",
                "spread_pct_vs_cl": f"{row['spread_pct_vs_cl']:.6f}" if row['spread_pct_vs_cl'] is not None else "",
            })


def write_json(rows, cl_map, bren_map):
    payload = {
        "meta": {
            "source": "Hyperliquid Info API",
            "dex": "xyz",
            "interval": "1d",
            "updated_at": datetime.now(tz=timezone.utc).isoformat(),
            "symbols": {
                "cl": COINS["cl"],
                "bren": COINS["bren"],
            },
            "counts": {
                "cl_days": len(cl_map),
                "bren_days": len(bren_map),
                "overlap_days": len(rows),
            },
        },
        "series": {
            "dates": [r["date"] for r in rows],
            "cl_close": [r["cl_close"] for r in rows],
            "bren_close": [r["bren_close"] for r in rows],
            "spread_abs_bren_minus_cl": [r["spread_abs_bren_minus_cl"] for r in rows],
            "spread_pct_vs_cl": [r["spread_pct_vs_cl"] for r in rows],
        },
        "rows": rows,
    }
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    cl_map = fetch_daily_candles(COINS["cl"])
    bren_map = fetch_daily_candles(COINS["bren"])
    rows = build_spread_rows(cl_map, bren_map)
    write_csv(rows)
    write_json(rows, cl_map, bren_map)
    print(json.dumps({
        "cl_days": len(cl_map),
        "bren_days": len(bren_map),
        "overlap_days": len(rows),
        "first_overlap": rows[0]["date"] if rows else None,
        "last_overlap": rows[-1]["date"] if rows else None,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
