# ============================================================
# scraper/utils/progress_tracker.py
# Persistent progress tracking — enables resume after interruption
# ============================================================

import json
from pathlib import Path
from datetime import datetime
from scraper.utils.logger import log


class ProgressTracker:
    """
    Saves scraping progress to disk so sessions can be resumed
    after crash or manual interruption.
    """

    def __init__(self, session_id: str, state_path: str = "data/raw"):
        self.session_id = session_id
        self.path = Path(state_path) / f"progress_{session_id}.json"
        self.state: dict = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                completed = len(data.get("completed_queries", []))
                log.info(f"Resuming session '{self.session_id}': {completed} queries already done.")
                return data
            except Exception as e:
                log.warning(f"Could not load progress file: {e}")
        return {
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "completed_queries": [],
            "total_records_scraped": 0,
            "last_updated": None,
        }

    def save(self):
        self.state["last_updated"] = datetime.now().isoformat()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def mark_query_done(self, query: str, records_found: int = 0):
        if query not in self.state["completed_queries"]:
            self.state["completed_queries"].append(query)
        self.state["total_records_scraped"] += records_found
        self.save()

    def is_query_done(self, query: str) -> bool:
        return query in self.state["completed_queries"]

    def get_stats(self) -> dict:
        return {
            "completed": len(self.state["completed_queries"]),
            "total_scraped": self.state["total_records_scraped"],
            "started_at": self.state["started_at"],
        }

    def reset(self):
        self.path.unlink(missing_ok=True)
        self.state = {
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "completed_queries": [],
            "total_records_scraped": 0,
            "last_updated": None,
        }
        log.info(f"Progress reset for session '{self.session_id}'.")
