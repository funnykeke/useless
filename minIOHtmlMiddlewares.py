from scrapy import signals

from minio import Minio
from minio.error import S3Error
import io

from datetime import datetime

class MinIOHtmlAskNatureMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    def __init__(self, minIO_uri, access_key,secret_key):
        self.minIO_uri = minIO_uri
        self.access_key = access_key
        self.secret_key = secret_key
        self.client = Minio(self.minIO_uri, access_key=self.access_key, secret_key=self.secret_key, secure=False)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(
            minIO_uri = crawler.settings.get("MINIO_URI"),
            access_key = crawler.settings.get("MINIO_ACCESS_KEY"),
            secret_key = crawler.settings.get("MINIO_SECRET_KEY")
        )
        s.crawler=crawler
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_response(self, request, response, spider):
        return response

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        print('caseId',spider.task);
        caseId=spider.task['caseId']
        try:
            # found = self.client.bucket_exists()
            fileTag=datetime.now().strftime('%Y%m')
            bytelist=response.body
            url=response.url
            tagName='/'.join([i for i in url.split('/')[3:] if i != ""])
            print('tagName',tagName);

            csv_buffer = io.BytesIO(bytelist)
            self.client.put_object("scbuk", fileTag+'/'+caseId+'/'+tagName+".html", data=csv_buffer,
                  length=len(bytelist),
                  content_type='text/html')

            self.crawler.stats.inc_value('save_html')
        except S3Error as e:
            print("error:", e)
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
