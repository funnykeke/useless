from scrapy.dupefilters import RFPDupeFilter


class CloseDupeFilter(RFPDupeFilter):
    def request_seen(self, request):
        return False
