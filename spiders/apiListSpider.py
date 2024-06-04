import re
import sys
from pathlib import Path
import logging

sys.path.extend((str(parent.absolute()) for parent in Path(__file__).parents))
import scrapy
import json
from tutorial.itemVo.apiPostDataVo import ApiPostDataItem

from scrapy.cmdline import execute


class ApiListSpider(scrapy.Spider):
    name = "apiList"
    post_ids = []
    # API 请求URL 地址
    askApiUrl = "https://kk25du67zi-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%20(lite)%203.27.1%3Binstantsearch.js%201.12.1%3BJS%20Helper%202.26.0&x-algolia-application-id=KK25DU67ZI&x-algolia-api-key=fa53954719a0c2ba8e1024642d0135e2"

    def __init__(self, taskInfo=None, *args, **kwargs):
        super(ApiListSpider, self).__init__(*args, **kwargs)
        if (taskInfo):
            self.task = json.loads(taskInfo)
            print('d', self.task)
        else:
            self.task = {}

    def start_requests(self):
        types = ["%3AInnovations", "%3AResources", "%3ACollections"]
        strategy_types = ['Break%20Down', 'Break%20Down%20Non-living%20Materials',
                          'Cooperate%20Between%20Different%20Species',
                          'Get%2C%20Store%2C%20or%20Distribute%20Resources', 'Maintain%20Community', 'Make', 'Modify',
                          'Move%20or%20Stay%20Put', 'Process%20Information', 'Protect%20From%20Physical%20Harm',
                          'Protect%20from%20living%20threats', 'Provide%20ecosystem%20services']
        for t in types:
            data = {
                "requests": [
                    {
                        "indexName": "asknature_searchable_posts",
                        "params": f"query=&hitsPerPage=50&maxValuesPerFacet=100&page=0&facetingAfterDistinct=true&facets=%5B%22taxonomies.sector%22%2C%22taxonomies.resource-type%22%2C%22taxonomies.audience%22%2C%22taxonomies.academic-subject%22%2C%22taxonomies.academic-standards%22%2C%22post_type_label%22%2C%22taxonomies_hierarchical.function.lvl0%22%2C%22taxonomies_hierarchical.system.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22post_type_label{t}%22%5D%5D"
                    },
                    {
                        "indexName": "asknature_searchable_posts",
                        "params": "query=&hitsPerPage=1&maxValuesPerFacet=100&page=0&facetingAfterDistinct=true&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=%5B%22post_type_label%22%5D"
                    }
                ]
            }
            yield scrapy.Request(url=self.askApiUrl, method='post', body=json.dumps(data),
                                 callback=self.parse,
                                 meta={'queryForm': json.dumps(data), 'page': 0})
        for t in strategy_types:
            data = {
                "requests": [
                    {
                        "indexName": "asknature_searchable_posts",
                        "params": f"query=&hitsPerPage=50&maxValuesPerFacet=100&page=0&facetingAfterDistinct=true&facets=%5B%22taxonomies.sector%22%2C%22taxonomies.resource-type%22%2C%22taxonomies.audience%22%2C%22taxonomies.academic-subject%22%2C%22taxonomies.academic-standards%22%2C%22post_type_label%22%2C%22taxonomies_hierarchical.function.lvl0%22%2C%22taxonomies_hierarchical.function.lvl1%22%2C%22taxonomies_hierarchical.system.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22taxonomies_hierarchical.function.lvl0%3A{t}%22%5D%2C%5B%22post_type_label%3ABiological%20Strategies%22%5D%5D"
                    },
                    {
                        "indexName": "asknature_searchable_posts",
                        "params": "query=&hitsPerPage=1&maxValuesPerFacet=100&page=0&facetingAfterDistinct=true&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=%5B%22post_type_label%22%5D&facetFilters=%5B%5B%22taxonomies_hierarchical.function.lvl0%3AMaintain%20Community%22%5D%5D"
                    },
                    {
                        "indexName": "asknature_searchable_posts",
                        "params": "query=&hitsPerPage=1&maxValuesPerFacet=100&page=0&facetingAfterDistinct=true&attributesToRetrieve=%5B%5D&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&analytics=false&clickAnalytics=false&facets=%5B%22taxonomies_hierarchical.function.lvl0%22%5D&facetFilters=%5B%5B%22post_type_label%3ABiological%20Strategies%22%5D%5D"
                    }
                ]
            }
            yield scrapy.Request(url=self.askApiUrl, method='post', body=json.dumps(data),
                                 callback=self.parse,
                                 meta={'queryForm': json.dumps(data), 'page': 0})

    def parse(self, response, **kwargs):
        result = response.json()['results'][0]
        page = response.meta['page']
        max_page = result['nbPages']
        hits = []
        hits.extend(result['hits'])
        for item in self.parseJsonItem(hits):
            yield item

        if page + 1 < max_page:
            page = page + 1
            queryForm = response.meta['queryForm']
            queryFormStr = re.sub(r'(?<=page=)\d+', str(page), queryForm)
            # queryForm = re.sub(r'(page=)\d+', rf'\1{page}', response.meta['queryForm'])
            yield scrapy.Request(url=self.askApiUrl, method='post', body=queryFormStr,
                                 callback=self.parse,
                                 meta={'queryForm': queryFormStr, 'page': page})

    def parseJsonItem(self, hits):
        postList = []
        for item in hits:
            if 'post_modified' not in item:
                continue
            else:
                if item['post_id'] in self.post_ids:
                    continue
                else:
                    self.post_ids.append(item['post_id'])
                postObj = ApiPostDataItem()
                postObj['permalink'] = item['permalink']
                postObj['postId'] = item['post_id']
                postObj['case_id'] = int(self.task['caseId'])
                postObj['objectId'] = item['objectID']
                postObj['content'] = item['content']
                postObj['subTitle'] = item['sub_title']
                postObj['summary'] = item['summary']
                postObj['postTypeLabel'] = item['singular_post_type_label']
                postObj['publicDate'] = item['public_date']
                postObj['thumbnailUrl'] = item['thumbnail_url'] if 'thumbnail_url' in item else ''

                taxonomies = item['taxonomies']
                taxonomies_hierarchical = item['taxonomies_hierarchical']

                if taxonomies_hierarchical:
                    postObj['taxonomies_hierarchical'] = taxonomies_hierarchical
                if taxonomies:
                    if 'function' in taxonomies:
                        postObj['functionNames'] = ','.join(taxonomies['function'])
                    if 'system' in taxonomies:
                        postObj['systemNames'] = ','.join(taxonomies['system'])

                    intype = taxonomies.get('innovation_type', None)
                    if intype:
                        postObj['innovationType'] = ','.join(intype)
                        logging.info(f"type:{postObj['innovationType']}")

                    keyword = item.get('keyword', None)
                    if keyword:
                        postObj['keyword'] = ','.join(keyword)

                    sdg = taxonomies.get('sdg', None)
                    if sdg:
                        postObj['sdg'] = ','.join(sdg)
                    sector = taxonomies.get('sector', None)
                    if sector:
                        postObj['sector'] = ','.join(sector)
                    stage = taxonomies.get('stage', None)
                    if stage:
                        postObj['stage'] = ','.join(stage)
                    technology = taxonomies.get('technology', None)
                    if technology:
                        postObj['technology'] = ','.join(technology)
                    academic_standards = taxonomies.get('academic-standards', None)
                    if academic_standards:
                        postObj['academic_standards'] = ','.join(academic_standards)
                    academic_subject = taxonomies.get('academic-subject', None)
                    if academic_subject:
                        postObj['academicSubject'] = ','.join(academic_subject)

                audience = item.get('audience', None)
                if audience:
                    postObj['audience'] = ','.join(audience)
                resourceType = item.get('resourceType', None)
                if resourceType:
                    postObj['resourceType'] = ','.join(resourceType)

                postObj['postModifiedInt'] = item["post_modified"]
                postObj['postDateInt'] = item["post_date"]
                postObj['postTitle'] = item["post_title"]
                postObj['postTypeLabel'] = item["post_type_label"]
                postObj['postType'] = item["post_type"]
                postObj['menuOrder'] = item["menu_order"]

                reference_sources = item.get('reference_sources', None)
                refList = []
                if reference_sources:
                    title = reference_sources["source_title"]

                    link = reference_sources["source_link"]
                    excerpt = reference_sources["source_excerpt"]
                    index = 0
                    for val in title:
                        refVal = {}
                        refVal['objectId'] = item['objectID']
                        refVal['sourceTitle'] = val
                        refVal['sourceLink'] = link[index]
                        refVal['sourceExcerpt'] = excerpt[index]
                        refList.append(refVal)
                        index = index + 1

                postList.append(postObj)
        return postList


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process command line arguments')
    parser.add_argument('--case_id', type=str, help='Case ID parameter')
    args = parser.parse_args()
    case_id = args.case_id
    par = {
        "caseId": case_id,
    }
    execute(['scrapy', 'crawl', 'apiList', '-a', "taskInfo=" + json.dumps(par)])
