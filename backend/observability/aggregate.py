from collections import defaultdict


def aggregate_by_case(rows):
    totals = defaultdict(lambda: {"calls": 0, "input_tokens": 0, "output_tokens": 0, "latency_ms": 0.0,
                                  "retries": 0, "cache_hits": 0, "cost_usd": 0.0,
                                  "known_cost_usd": 0.0, "unknown_cost_calls": 0,
                                  "missing_usage_calls": 0})
    for row in rows:
        out = totals[row["case_id"]]
        out["calls"] += 1
        for key in ("input_tokens", "output_tokens", "latency_ms", "retries"):
            out[key] += row.get(key, 0) or 0
        cost = row.get("cost_usd")
        if cost is None:
            out["unknown_cost_calls"] += 1
        else:
            out["known_cost_usd"] += cost
        out["cost_usd"] = None if out["unknown_cost_calls"] else out["known_cost_usd"]
        out["missing_usage_calls"] += any(row.get(key) is None for key in ("input_tokens", "output_tokens"))
        out["cache_hits"] += row.get("cache_status") == "hit"
    return dict(totals)


def aggregate_overall(case_totals):
    result = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "latency_ms": 0.0,
              "retries": 0, "cache_hits": 0, "cost_usd": 0.0,
              "known_cost_usd": 0.0, "unknown_cost_calls": 0, "missing_usage_calls": 0}
    for total in case_totals.values():
        for key in result:
            if key != "cost_usd":
                result[key] += total.get(key, 0)
    result["cost_usd"] = None if result["unknown_cost_calls"] else result["known_cost_usd"]
    return result
