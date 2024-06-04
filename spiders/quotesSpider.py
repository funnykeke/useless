import sys
from pathlib import Path

sys.path.extend((str(parent.absolute()) for parent in Path(__file__).parents))
import scrapy

from tutorial.itemVo.items import TutorialItem

from scrapy.crawler import CrawlerProcess
from multiprocessing import Process
import logging
from scrapy.cmdline import execute

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self, caseId=None, *args, **kwargs):
        super(QuotesSpider, self).__init__(*args, **kwargs)
        self.caseId = int(caseId)

    def start_requests(self):
        urls = [
            'https://asknature.org/strategy/shell-growth-through-compartmentalization/',
        ]
        logging.warning("This is a warning")
        self.logger.info(f'{self.caseId}任务启动了')
        for url in urls:
            self.logger.info("Parse function called on %s", url)
            self.crawler.stats.inc_value('parse_url')
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]

        item = TutorialItem()
        url = response.xpath('/html/head/meta[@property="og:url"]').attrib['content']
        description = response.xpath('/html/head/meta[@property="og:description"]').attrib['content']
        title = response.xpath('/html/head/meta[@property="og:title"]').attrib['content']
        dept = response.xpath('//*[@id="post-content"]/div[1]/q/text()').extract();

        txt = response.xpath('//div[@class="wrap text-wrap wide lite-top align-center"]')
        animal = txt.xpath('h3/text()').extract();
        type = response.xpath('//*[@id="content"]/section[1]/div[4]/small/text()').extract()

        author = response.xpath('//*[@id="content"]/section[1]/div[6]/p/text()').extract()

        secName = response.xpath('//*[@id="content"]/section[1]/div[5]/div/h2/text()').extract()

        Introduction = response.xpath('//*[@id="post-content"]/article[1]/div[2]/p/text()').extract()

        timg = response.xpath('//*[@id="post-content"]/article[2]/div[2]/div/div/div/div[1]/div/a/img').attrib[
            'data-src']

        item['dept'] = dept[0]
        item['name2'] = secName[0]
        item['introduction'] = Introduction[0]
        item['timg'] = timg
        item['title'] = title
        item['description'] = description
        item['url'] = url
        item['animal'] = animal[0]
        item['type'] = type[0]
        item['author'] = author[0]
        logging.warning("解析得到一条")
        self.crawler.stats.inc_value('parse_html')
        return item


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process command line arguments')
    parser.add_argument('--case_id', type=str, help='Case ID parameter')
    args = parser.parse_args()
    case_id = args.case_id
    execute(['scrapy', 'crawl', 'quotes', '-a', case_id])