# -*- coding: utf-8 -*-

# Scrapy settings for medical_crawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'medical_crawler'
LOG_LEVEL = 'ERROR'

SPIDER_MODULES = ['medical_crawler.spiders']
NEWSPIDER_MODULE = 'medical_crawler.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'medical_crawler (+http://www.yourdomain.com)'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.defaultheaders.DefaultHeadersMiddleware': 100,
}

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.103 Safari/537.36'
}

ITEM_PIPELINES = {
    'medical_crawler.pipelines.A120askPipeline': 300,
}

DOWNLOAD_DELAY = 1
