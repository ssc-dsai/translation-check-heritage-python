BOT_NAME = 'websites'
SPIDER_MODULES = ['websites.spiders']
NEWSPIDER_MODULE = 'websites.spiders'

# User agent
USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 64

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'websites.middlewares.WebsitesDownloaderMiddleware': 543,
}

DOWNLOADER_MIDDLEWARES.update({
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy_cookies.downloadermiddlewares.cookies.CookiesMiddleware': 700,
})

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'websites.pipelines.SaveDBPipeline': 300,
}

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = False
HTTPCACHE_EXPIRATION_SECS = 186400
HTTPCACHE_DIR = 'httpcachenew'


# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

REDIRECT_ENABLED = True

AUTOTHROTTLE_ENABLED = True
CONNECTION_STRING = 'sqlite:///data/websites.db'

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

LOG_LEVEL = 'WARNING'
