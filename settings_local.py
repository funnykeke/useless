# Scrapy settings for tutorial project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "tutorial"

SPIDER_MODULES = ["tutorial.spiders"]
NEWSPIDER_MODULE = "tutorial.spiders"

ROBOTSTXT_OBEY = False
# 日志等级
# LOG_LEVEL = 'DEBUG'
# # 定义日志输出文件
# LOG_FILE = 'tutorial.log'
# # 线程数
CONCURRENT_REQUESTS = 3
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16
# 请求头
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58'
}
# 下载延时
# DOWNLOAD_DELAY = 3
# 禁用cookie
COOKIES_ENABLED = False
# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "tutorial.middlewares.TutorialSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "tutorial.middlewares.TutorialDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 408]
RETRY_TIMES = 6
# DOWNLOAD_TIMEOUT = 60

ITEM_PIPELINES = {
    'tutorial.pipelines.mongoPipeline.MongoPipeline': 300,
    # 'tutorial.pipelines.fileDownloadPipeline.FileDownPipeline': 200,
}
SPIDER_MIDDLEWARES = {
    # 'tutorial.minIOHtmlMiddlewares.MinIOHtmlAskNatureMiddleware': 543
    # "tutorial.middlewares.ProxyMiddleware": 543
}

EXTENSIONS = {
    "scrapy.extensions.corestats.CoreStats": None,
    "tutorial.extensions.stats_log_core.StatsLogCore": 300
}

MONGO_URI = 'mongodb://bionics_kn:bionics_kn123@192.168.1.101:27017/test_db?authSource=bionics_kn_db&retryWrites=true&w=majority'
MONGO_DATABASE = 'bionics_kn_db'

MYSQL_HOST = '192.168.1.101'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'qwer1234'
MYSQL_DATABASE = 'strategy_as_dev_db'

MINIO_URI = '192.168.1.101:9000'
MINIO_ACCESS_KEY = 'admin'
MINIO_SECRET_KEY = 'qwer1234'

# IMAGES_STORE = 's3://118.178.237.91:32400/scimgbuk/images'
# FILES_STORE = 's3://118.178.237.91:32400/scimgbuk/images'
# FILES_STORE_S3_ACL='private'
# # IMAGES_STORE = '/Users/scoder/Documents/bb'
# #
# AWS_ENDPOINT_URL = 'http://118.178.237.91:32400'
# AWS_BUCKET_NAME = 'scimgbuk'
# # # IMAGES_STORE = '/Users/scoder/Documents/bb'
# AWS_ACCESS_KEY_ID = 'au_minio_root'
# AWS_SECRET_ACCESS_KEY = 'minio!rootau12306'
#
# # IMAGES_STORE = 's3://scimgbuk/images'
# IMAGES_STORE = 's3://scimgbuk/images'
# IMAGES_STORE_S3_ACL = 'private'
#
AWS_USE_SSL = False  # or True (None by default)
AWS_VERIFY = False  # or True (None by default)

# s3store.AWS_ACCESS_KEY_ID = settings["AWS_ACCESS_KEY_ID"]
# s3store.AWS_SECRET_ACCESS_KEY = settings["AWS_SECRET_ACCESS_KEY"]
# s3store.AWS_SESSION_TOKEN = settings["AWS_SESSION_TOKEN"]
# s3store.AWS_ENDPOINT_URL = settings["AWS_ENDPOINT_URL"]
# s3store.AWS_REGION_NAME = settings["AWS_REGION_NAME"]
# s3store.AWS_USE_SSL = settings["AWS_USE_SSL"]
# s3store.AWS_VERIFY = settings["AWS_VERIFY"]
# s3store.POLICY = settings["FILES_STORE_S3_ACL"]

REDIS = {
    'host': '192.168.1.101',
    'port': 6379,
    'password': 'qwer1234'
}
