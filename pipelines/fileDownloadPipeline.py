from tutorial.itemVo.ImageVo import ImageVo, ImageCredit, HeadImageVo
import scrapy
from datetime import datetime
from minio import Minio
import io
from scrapy.pipelines.files import FilesPipeline
from pathlib import PurePosixPath
from urllib.parse import urlparse
from scrapy.utils.misc import md5sum

from tutorial.itemVo.fileVo import FileVo


class FileDownPipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        fileTag = datetime.now().strftime('%Y%m')
        spider_name = self.crawler.spider.name
        ctx_path = PurePosixPath(urlparse(request.url).path).name
        return f"{spider_name}/{fileTag}/{ctx_path}"

    def find_file_links(self, data):
        excluded_types = (str, int, float, tuple, bool, type(None))
        file_links = []

        def _find_file_classes(obj):
            if isinstance(obj, ImageVo):
                file_links.append(obj.src)
            elif isinstance(obj, ImageCredit):
                file_links.append(obj.url)
            elif isinstance(obj, HeadImageVo):
                file_links.append(obj.src)
            elif isinstance(obj, FileVo):
                file_links.append(obj.src)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    _find_file_classes(value)
            elif isinstance(obj, list):
                for item in obj:
                    _find_file_classes(item)
            elif isinstance(obj, object) and not isinstance(obj, excluded_types):
                for value in obj.__dict__.values():
                    _find_file_classes(value)

        _find_file_classes(data._values)
        return file_links

    index = 0

    def parse_file_links(self, data, img_paths):
        excluded_types = (str, int, float, tuple, bool, type(None))

        def _parse_file_classes(obj):
            if isinstance(obj, ImageVo):
                obj.path = img_paths[self.index]
                self.index = self.index + 1
            elif isinstance(obj, ImageCredit):
                obj.path = img_paths[self.index]
                self.index = self.index + 1
            elif isinstance(obj, HeadImageVo):
                obj.path = img_paths[self.index]
                self.index = self.index + 1
            elif isinstance(obj, FileVo):
                obj.path = img_paths[self.index]
                self.index = self.index + 1
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    _parse_file_classes(value)
            elif isinstance(obj, list):
                for item in obj:
                    _parse_file_classes(item)
            elif isinstance(obj, object) and not isinstance(obj, excluded_types):
                for value in obj.__dict__.values():
                    _parse_file_classes(value)

        _parse_file_classes(data._values)
        return data

    def get_media_requests(self, item, info):
        img_links = self.find_file_links(item)
        for link in img_links:
            yield scrapy.Request(link)

    def __init__(self, minIO_uri, access_key, secret_key, settings):
        super(FileDownPipeline, self).__init__(store_uri=None, settings=settings)
        self.minIO_uri = minIO_uri
        self.access_key = access_key
        self.secret_key = secret_key

        # 初始化 后缀
        self.jpgimg = ['.jpg', '.jpeg']
        self.pngimg = ['.png']
        self.offile = ['.doc', '.docx', '.xls', '.xlsx']
        self.pdffile = ['.pdf']

        self.allfile = []
        self.allfile.extend(self.jpgimg)
        self.allfile.extend(self.pngimg)
        self.allfile.extend(self.offile)
        self.allfile.extend(self.pdffile)

        self.fail_urls = []

        self.client = Minio(self.minIO_uri, access_key=self.access_key, secret_key=self.secret_key, secure=False)

    @classmethod
    def from_crawler(cls, crawler):
        pipe = cls(
            minIO_uri=crawler.settings.get("MINIO_URI"),
            access_key=crawler.settings.get("MINIO_ACCESS_KEY"),
            secret_key=crawler.settings.get("MINIO_SECRET_KEY"),
            settings=crawler.settings
        )
        pipe.crawler = crawler
        pipe._fingerprinter = crawler.request_fingerprinter
        return pipe

    def item_completed(self, results, item, info):
        # image_paths = [x['path'] for ok, x in results if ok]
        paths = [x['path'] if ok else '' for ok, x in results]
        self.index = 0
        item = self.parse_file_links(item, paths)
        return item

    def media_failed(self, failure, request, info):
        self.fail_urls.append(request.url)
        info.spider.crawler.stats.set_value('download_failed_url', self.fail_urls)
        info.spider.crawler.stats.inc_value('download_failed_url_count')

    def file_downloaded(self, response, request, info, *, item=None):
        path = self.file_path(request, response=response, info=info, item=item)
        # key = response.meta['key']
        # item[key + '_href'] = path

        buf = io.BytesIO(response.body)
        buflen = len(response.body)
        checksum = md5sum(buf)
        buf.seek(0)
        if any(substring in path for substring in self.pngimg):
            contentType = 'image/png'
        elif any(substring in path for substring in self.jpgimg):
            contentType = 'image/jpeg'
        elif any(substring in path for substring in self.pdffile):
            contentType = 'image/pdf'
        elif any(substring in path for substring in self.offile):
            contentType = 'image/msword'
        else:
            contentType = 'image/octet-stream'

        self.client.put_object("scimgbuk", path, data=buf,
                               length=buflen,
                               content_type=contentType)
        return checksum
