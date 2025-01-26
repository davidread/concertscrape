from collections import defaultdict
from enum import Enum, auto


class ScrapeResult(Enum):
    NEW = auto()
    EXISTING = auto()
    ERROR = auto()

class ScrapingStats:
    def __init__(self):
        self.stats = defaultdict(lambda: {result: 0 for result in ScrapeResult})
        self.errored = False
        
    def add_concert(self, id_, result):
        self.stats[id_][result] += 1
        if result == ScrapeResult.ERROR:
            self.errored = True
    
    def print_summary(self):
        print("\n=== Scraping Summary ===")
        total_by_result = defaultdict(int)
        
        def print_summary_for_id(id_, total, new, existing, errors):
            print(f"\n{id_}:")
            print(f"  Total concerts found: {total}")
            print(f"  New concerts recorded: {new} ({(new/total * 100):.1f}%)")
            print(f"  Existing concerts: {existing}")
            if errors:
                print(f"  ERRORS: {errors} ({(errors/total * 100):.1f}%)")

        for id_, counts in self.stats.items():
            total = sum(counts.values())
            
            print_summary_for_id(id_, total, counts[ScrapeResult.NEW], counts[ScrapeResult.EXISTING], counts[ScrapeResult.ERROR])
            
            for result, count in counts.items():
                total_by_result[result] += count
        
        if len(self.stats) > 1:
            print_summary_for_id("Overall Summary", sum(total_by_result.values()), total_by_result[ScrapeResult.NEW], total_by_result[ScrapeResult.EXISTING], total_by_result[ScrapeResult.ERROR])
        print("=====================")