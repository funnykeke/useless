import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from scrapy import Spider

import logging

from scrapy.statscollectors import StatsCollector
if TYPE_CHECKING:
    from scrapy.crawler import Crawler

logger = logging.getLogger(__name__)


StatsT = Dict[str, Any]

class ParseStatsCollector(StatsCollector):
    def __init__(self, crawler: "Crawler"):
        super().__init__(crawler)
        self.spider_stats: Dict[str, StatsT] = {}

    def _persist_stats(self, stats: StatsT, spider: Spider) -> None:
        self.spider_stats[spider.name] = stats

