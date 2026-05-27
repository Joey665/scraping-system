# ============================================================
# scraper/core/orchestrator.py
# Main scraping orchestrator — coordinates all components
# ============================================================

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from tqdm import tqdm

from config.keywords import generate_all_search_queries, get_all_queries
from config.settings import settings
from scraper.core.browser import BrowserManager
from scraper.core.maps_scraper import MapsSearchScraper
from scraper.core.models import EstateRecord
from scraper.utils.deduplicator import Deduplicator
from scraper.utils.progress_tracker import ProgressTracker
from scraper.utils.logger import log
from scraper.exporters.exporter import export_to_csv, export_to_excel, save_raw_json
from leads.scorer import score_all_records


class ScraperOrchestrator:
    """
    Top-level coordinator.
    Handles: query batching, concurrency control, progress tracking,
    deduplication, scoring, and export.
    """

    def __init__(self, session_id: Optional[str] = None, states: Optional[list[str]] = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.states = states or ["Lagos", "Abuja"]
        self.progress = ProgressTracker(self.session_id)
        self.deduplicator = Deduplicator()
        self.all_records: list[EstateRecord] = []

    async def run(self, batch_size: Optional[int] = None):
        """Main entry point. Runs full scraping pipeline."""
        batch_size = batch_size or settings.SCRAPER_BATCH_SIZE
        queries = []

        for state in self.states:
            queries.extend(generate_all_search_queries(state))

        # Filter already-completed queries (resume support)
        remaining = [q for q in queries if not self.progress.is_query_done(q["query"])]
        total = len(queries)
        done_count = total - len(remaining)
        log.info(f"Session '{self.session_id}': {total} total queries, {done_count} already done, {len(remaining)} remaining.")

        if not remaining:
            log.info("All queries already completed. Nothing to scrape.")
            return

        # Batch the remaining queries
        batches = [remaining[i:i+batch_size] for i in range(0, len(remaining), batch_size)]
        log.info(f"Starting scrape in {len(batches)} batches of ≤{batch_size}.")

        async with BrowserManager() as browser:
            scraper = MapsSearchScraper(browser)

            with tqdm(total=len(remaining), desc="Scraping Progress", unit="query") as pbar:
                for batch_idx, batch in enumerate(batches):
                    log.info(f"--- Batch {batch_idx+1}/{len(batches)} ({len(batch)} queries) ---")

                    # Concurrent tab limit from settings
                    sem = asyncio.Semaphore(settings.SCRAPER_CONCURRENT_TABS)

                    async def scrape_with_sem(q):
                        async with sem:
                            try:
                                results = await scraper.search_query(
                                    query=q["query"],
                                    state=q["state"],
                                    area=q["area"],
                                    keyword=q["keyword"],
                                )
                                self.progress.mark_query_done(q["query"], len(results))
                                return results
                            except Exception as e:
                                log.error(f"Query failed: {q['query']} — {e}")
                                return []

                    tasks = [scrape_with_sem(q) for q in batch]
                    batch_results = await asyncio.gather(*tasks)

                    for results in batch_results:
                        new_records = self.deduplicator.filter_new(results)
                        self.all_records.extend(new_records)
                        pbar.update(1)

                    # Save checkpoint after each batch
                    self._save_checkpoint()
                    log.info(f"Batch {batch_idx+1} complete. Total records so far: {len(self.all_records):,}")

        log.info(f"Scraping complete. Total unique records: {len(self.all_records):,}")
        await self._post_process()

    def _save_checkpoint(self):
        """Save current records to raw JSON as a checkpoint."""
        if self.all_records:
            save_raw_json(self.all_records, f"{self.session_id}_checkpoint")

    async def _post_process(self):
        """Score leads and export all output files."""
        log.info("Running lead scoring...")
        self.all_records = score_all_records(self.all_records)

        hot = sum(1 for r in self.all_records if r.lead_tier == "HOT")
        warm = sum(1 for r in self.all_records if r.lead_tier == "WARM")
        cold = sum(1 for r in self.all_records if r.lead_tier == "COLD")
        log.info(f"Lead scoring complete: {hot} HOT | {warm} WARM | {cold} COLD")

        # Export
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = export_to_csv(self.all_records, f"bracken_all_leads_{ts}.csv")
        xlsx_path = export_to_excel(self.all_records, f"bracken_all_leads_{ts}.xlsx")
        save_raw_json(self.all_records, f"final_{ts}")

        log.info(f"✅ Export complete.")
        log.info(f"   CSV:   {csv_path}")
        log.info(f"   Excel: {xlsx_path}")

        return csv_path, xlsx_path


async def run_scraper(states: Optional[list[str]] = None, session_id: Optional[str] = None):
    """Convenience entry point."""
    orchestrator = ScraperOrchestrator(session_id=session_id, states=states)
    await orchestrator.run()
