# -*- coding: utf-8 -*-
from scrapy.http import HtmlResponse
from selenium import webdriver


class PhantomJSMiddleware(object):
    @classmethod
    def process_request(cls, request, spider):
        if request.meta.get('PhantomJS', None):
            driver = webdriver.PhantomJS()
            driver.get(request.url)
            content = driver.page_source.encode('utf-8')
            driver.quit()
            return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)
