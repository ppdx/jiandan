# -*- coding: utf-8 -*-
import re
import sqlite3
from urllib.parse import urljoin
import logging

import scrapy
from scrapy.utils.project import get_project_settings

import jiandan
from jiandan.items import *
from .pic import PicSpider


def is_number(s):
    try:
        int(s)
        return True
    except:
        return False


class OoxxSpider(scrapy.Spider):
    """This spider only download images do NOT saving items."""
    name = "ooxx"
    allowed_domains = ["jandan.net"]

    def __init__(self, start=None, length=None, *args, **kwargs):
        super(OoxxSpider, self).__init__(*args, **kwargs)
        self.start = start if is_number(start) and int(start) > 0 else None

    def start_requests(self):
        if self.start is None:
            url = 'http://jandan.net/ooxx'
        else:
            url = 'http://jandan.net/ooxx/page-' + str(self.start)
        request = scrapy.Request(url, self.parse, headers={
                                 "Host": "jandan.net"})
        request.meta['PhantomJS'] = True
        yield request

    def parse(self, response):
        logging.info("has crawled %s", response.url)
        for sel in response.xpath('//li[starts-with(@id, "comment-")]'):
            images = sel.css('img::attr(src)').extract()
            for uri in images:
                yield ImageItem(uri=urljoin(response.url, uri))

        next_url = response.css(
            '.previous-comment-page').xpath('@href').extract()[0]
        next_url = urljoin(response.url, next_url)
        request = scrapy.Request(next_url, self.parse,
                                 headers={"Host": "jandan.net",
                                          "Referer": response.url, }
                                 )
        request.meta['PhantomJS'] = True
        yield request
