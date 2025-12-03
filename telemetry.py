import json
import os
from datetime import datetime

LOG_PATH = "logs/requests.log"


def log_request(pathway: str,
                latency: float,
                tokens: int | None,
                cost: float | None,
                mode: str,
                error: str | None = None):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "pathway": pathway,  # 'rag' / 'tool' / 'none'
        "mode": mode,        # 'qa' / 'quiz'
        "latency_sec": latency,
        "tokens": tokens,
        "cost": cost,
        "error": error,
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")