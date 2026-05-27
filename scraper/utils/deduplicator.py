# ============================================================
# scraper/utils/deduplicator.py
# Persistent deduplication using a local hash registry
# ============================================================

import json
import xxhash
from pathlib import Path
from scraper.utils.logger import log


class Deduplicator:
    """
    Tracks already-scraped places across sessions using a JSON hash store.
    Keys on: place_id > maps_url > (name + address) combo.
    """

    def __init__(self, registry_path: str = "data/raw/dedup_registry.json"):
        self.registry_path = Path(registry_path)
        self.seen_hashes: set[str] = set()
        self._load()

    def _load(self):
        if self.registry_path.exists():
            try:
                data = json.loads(self.registry_path.read_text(encoding="utf-8"))
                self.seen_hashes = set(data.get("hashes", []))
                log.info(f"Deduplicator loaded {len(self.seen_hashes):,} known records.")
            except Exception as e:
                log.warning(f"Could not load dedup registry: {e}. Starting fresh.")
        else:
            log.info("No dedup registry found. Starting fresh.")

    def save(self):
        """Persist current registry to disk."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.write_text(
            json.dumps({"hashes": list(self.seen_hashes)}, indent=2),
            encoding="utf-8",
        )

    def _make_hash(self, record: dict) -> str:
        """Create a stable fingerprint from a record."""
        # Priority: place_id → maps_url → name+address
        key = (
            record.get("place_id")
            or record.get("maps_url")
            or f"{record.get('name', '')}|{record.get('address', '')}"
        )
        return xxhash.xxh64(key.lower().strip()).hexdigest()

    def is_duplicate(self, record: dict) -> bool:
        h = self._make_hash(record)
        return h in self.seen_hashes

    def mark_seen(self, record: dict):
        h = self._make_hash(record)
        self.seen_hashes.add(h)

    def filter_new(self, records: list[dict]) -> list[dict]:
        """Return only records not seen before, and mark them."""
        new = []
        for r in records:
            if not self.is_duplicate(r):
                new.append(r)
                self.mark_seen(r)
        log.info(f"Deduplication: {len(records)} in → {len(new)} new ({len(records) - len(new)} dupes skipped)")
        self.save()
        return new


deduplicator = Deduplicator()
