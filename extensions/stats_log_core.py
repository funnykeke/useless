import json
import logging
from datetime import datetime, timezone

from scrapy import signals
from threading import Timer

from scrapy.extensions.logstats import LogStats
import logging
import redis
from tutorial.utils.complex_encoder import ComplexEncoder


class StatsLogCore:
    def __init__(self, crawler, dbparams, redis_params, interval):
        self.exit_code = False
        self.stats = crawler.stats
        self.interval = interval
        self.multiplier = 60.0 / self.interval
        self.crawler = crawler

        # TODO 初始化数据库 mysqlClient
        self.stats_keys = set()
        self.cur_d = {

        }

        self.redisClient = redis.Redis(
            host=redis_params['host'],
            port=redis_params['port'],
            password=redis_params['password'],
            decode_responses=True, charset='utf-8', encoding='utf-8'
        )

    @classmethod
    def from_crawler(cls, crawler):
        dbparams = crawler.settings.get("MYSQL")
        redis_params = crawler.settings.get("REDIS")
        interval = crawler.settings.get("INTERVAL", 1)
        ext = cls(crawler, dbparams, redis_params, interval)

        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.engine_started, signal=signals.engine_started)
        crawler.signals.connect(ext.engine_stopped, signal=signals.engine_stopped)
        crawler.signals.connect(ext.response_received, signal=signals.response_received)
        return ext

    def spider_opened(self, spider):
        self.spider=spider
        self.pagesprev = 0
        self.itemsprev = 0

        self.start_time = datetime.now(tz=timezone.utc)
        self.stats.set_value("start_time", self.start_time, spider=spider)

        mysql_d = {
            "caseId":spider.task['caseId'],
            "measurement": "spider_opened",
            "time": datetime.now(tz=timezone.utc),
            'spider_name': self.crawler.spider.name,
            "fields": {
                'start_time': datetime.now(tz=timezone.utc),
                'spider_name': spider.name,
                'task_info': json.dumps(spider.task)
            }
        }

        # TODO 保存到数据库
        logging.info('爬虫开始了，保存日志')

    def spider_closed(self, spider, reason):
        finish_time = datetime.now(tz=timezone.utc)
        elapsed_time = finish_time - self.start_time
        elapsed_time_seconds = elapsed_time.total_seconds()
        self.stats.set_value(
            "elapsed_time_seconds", elapsed_time_seconds, spider=spider
        )
        self.stats.set_value("finish_time", finish_time, spider=spider)
        self.stats.set_value("finish_reason", reason, spider=spider)
        total_items_scraped = self.stats.get_value('item_scraped_count')
        logging.info(f'爬虫关闭了，处理了 {total_items_scraped} 个item，保存日志')

        mongoDBName = '' if not hasattr(spider, 'mongodbCname') else spider.mongodbCname
        task_rp = {
            "caseId": spider.task['caseId'],
            "taskId": '',
            "stepId": '',
            # "taskId": spider.task['taskId'],
            # "stepId": spider.task['stepId'],
            # "jobId": spider.task['jobId'],
            "mongodbCname": mongoDBName,
            "code": '0000',
            "time": datetime.now(tz=timezone.utc),
        }
        self.publish('parserTask', json.dumps(task_rp, cls=ComplexEncoder))

        statsLog = {
            "caseId": spider.task['caseId'],
            "measurement": "spider_closed",
            "time": datetime.now(tz=timezone.utc),
            'spider_name': self.crawler.spider.name,
            "fields": {
                'finish_time': self.stats.get_value('finish_time'),
                'spider_name': spider.name,
                'finish_reason': self.stats.get_value('finish_reason'),
                'download_failed_url_count':self.stats.get_value('download_failed_url_count'),
                'download_failed_url':self.stats.get_value('download_failed_url')
            }
        }
        self.publish('statsCoreLog', json.dumps(statsLog, cls=ComplexEncoder))
        # 最后上包失败的数据


    def publish(self,channel,message):
        self.redisClient.publish(channel,message)

    def engine_started(self):
        Timer(self.interval, self.handler_sta,(self.spider,)).start()
        logging.info('Engine 开始')

    def engine_stopped(self):
        self.exit_code = True
        logging.info('Engine 退出了')

    def item_scraped(self, item, spider):
        self.stats.inc_value("item_scraped_count", spider=spider)

    def response_received(self, spider):
        self.stats.inc_value("response_received_count", spider=spider)

    def item_dropped(self, item, spider, exception):
        reason = exception.__class__.__name__
        self.stats.inc_value("item_dropped_count", spider=spider)
        self.stats.inc_value(f"item_dropped_reasons_count/{reason}", spider=spider)

    def handler_sta(self,spider):
        logging.info('定时执行保存统计数据')

        statsLog = {
            "caseId": spider.task['caseId'],
            "measurement": "spider_opened",
            "time": datetime.now(tz=timezone.utc),
            'spider_name': self.crawler.spider.name,
            "fields": {
                'start_time': datetime.now(tz=timezone.utc),
                'spider_name': self.crawler.spider.name,
                'scheduler':{
                    'enqueued':self.stats.get_value("scheduler/enqueued"),
                    'dequeued':self.stats.get_value("scheduler/dequeued")
                },
                'downloader':{
                    'request_count': self.stats.get_value("downloader/request_count"),
                    'request_bytes': self.stats.get_value("downloader/request_bytes"),
                    'response_count': self.stats.get_value("downloader/response_count"),
                    'response_status_count': self.stats.get_value("downloader/response_status_count/200"),
                    'response_bytes': self.stats.get_value("downloader/response_bytes")
                },
                'response_received_count': self.stats.get_value("response_received_count"),
                'file_count': self.stats.get_value("file_count"),
                'spider_exceptions': self.stats.get_value("spider_exceptions"),
                'elapsed_time_seconds': self.stats.get_value("elapsed_time_seconds")
            }
        }
        self.publish('statsCoreLog', json.dumps(statsLog, cls=ComplexEncoder))

        if not self.exit_code:
            Timer(self.interval, self.handler_sta,(spider,)).start()
