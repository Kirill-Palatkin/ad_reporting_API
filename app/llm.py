import os
from dotenv import load_dotenv

load_dotenv()

USE_LLM = os.getenv("USE_LLM", "0") == "1"


def explain_summary(metrics: dict):
    if metrics.get("status") != "ok":
        return "Недостаточно данных"
    if USE_LLM:
        return f"CTR показывает долю кликов ({metrics.get('ctr')*100:.2f}%), а CPC — среднюю стоимость клика ({metrics.get('cpc')}); вместе метрики отражают эффективность."
    else:
        ctr = metrics.get("ctr")*100 if metrics.get("ctr") is not None else "N/A"
        cpc = metrics.get("cpc") if metrics.get("cpc") is not None else "N/A"
        return f"CTR={ctr}%, CPC={cpc}; данных достаточно."
