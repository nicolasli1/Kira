import json
import os
from datetime import datetime, timezone
from pathlib import Path


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


record = {
    "deployment_timestamp": iso_now(),
    "workflow": os.getenv("GITHUB_WORKFLOW", "local"),
    "run_id": os.getenv("GITHUB_RUN_ID", "local"),
    "sha": os.getenv("GITHUB_SHA", "local"),
    "ref": os.getenv("GITHUB_REF_NAME", "local"),
    "lead_time_seconds": os.getenv("LEAD_TIME_SECONDS", "unknown"),
    "deployment_frequency_window": "per successful workflow run",
    "change_failure_rate_source": "derived from workflow conclusion and post-deploy test failures",
    "mttr_source": "derived from time between failed run and next successful recovery run",
}

output_path = Path("dora-metrics.json")
output_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
