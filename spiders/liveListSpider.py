import sys
from pathlib import Path

sys.path.extend((str(parent.absolute()) for parent in Path(__file__).parents))
import scrapy

import json

from scrapy.cmdline import execute
from scrapy.utils.project import get_project_settings

from tutorial.itemVo.liveSystemItemVo import LiveSystemItem
from tutorial.itemVo.functionItemVo import FunctionItem
from tutorial.utils.utils import MySQLUtil



class LiveingSystemSpider(scrapy.Spider):
    name = "live"

    def __init__(self, taskInfo=None, *args, **kwargs):
        super(LiveingSystemSpider, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        if (taskInfo):
            self.task = json.loads(taskInfo)
            print('d', self.task)
        else:
            self.task = {}
        self.mysql_util = MySQLUtil(settings.get('MYSQL_HOST'), settings.get('MYSQL_PORT'),
                                    settings.get('MYSQL_USER'), settings.get('MYSQL_PASSWORD'),
                                    settings.get('MYSQL_DATABASE'))

    def start_requests(self):
        urls = [
            'https://asknature.org/?s=&page=0&hFR%5Bpost_type_label%5D%5B0%5D=Biological%20Strategies&is_v=1',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        url = response.xpath('//*[@id="content"]/script[8]/text()').extract()[0].replace('\n', '')

        txtval = url.split('var system_terms =');
        function_terms = txtval[0].replace('var function_terms =', '')
        function_terms = function_terms.replace(';', '')

        system_terms = txtval[1].replace('var function_terms =', '')
        system_terms = system_terms.replace(';', '')

        function_terms = json.loads(function_terms, strict=False)

        for _, i in function_terms.items():
            fun = FunctionItem()
            fun['name'] = i['name']
            fun['objectId'] = i['id']
            fun['slug'] = i['slug']
            fun['description'] = i['description']
            fun['case_id'] = int(self.task['caseId'])
            yield fun

        system_terms = json.loads(system_terms, strict=False)
        for _, i in system_terms.items():
            ls = LiveSystemItem()
            ls['name'] = i['name']
            ls['objectId'] = i['id']
            ls['slug'] = i['slug']
            ls['description'] = i['description']
            ls['case_id'] = int(self.task['caseId'])
            yield ls


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Process command line arguments')
    parser.add_argument('--case_id', type=str, help='Case ID parameter')
    args = parser.parse_args()
    case_id = args.case_id
    par = {
        "caseId": case_id,
    }
    execute(['scrapy', 'crawl', 'live', '-a', "taskInfo=" + json.dumps(par)])