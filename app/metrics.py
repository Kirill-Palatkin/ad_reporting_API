def compute_metrics(impressions: int, clicks: int, cost: float):
    if not all(isinstance(x, (int, float)) for x in [impressions, clicks, cost]):
        return {"ctr": None, "cpc": None, "status": "no_answer"}
    if impressions <= 0 or clicks < 0 or cost < 0:
        return {"ctr": None, "cpc": None, "status": "no_answer"}
    try:
        ctr = clicks / impressions
        cpc = cost / clicks if clicks > 0 else None
        return {"ctr": ctr, "cpc": cpc, "status": "ok"}
    except ZeroDivisionError:
        return {"ctr": None, "cpc": None, "status": "no_answer"}
