# -*- coding: utf-8 -*-
import re
import sqlite3
from urllib.parse import urljoin

import scrapy
from scrapy.utils.project import get_project_settings

import jiandan
from jiandan.items import *


def is_number(s):
    try:
        int(s)
        return True
    except:
        return False


class PicSpider(scrapy.Spider):
    name = "pic"
    allowed_domains = ["jandan.net"]

    def __init__(self, start=None, length=None, *args, **kwargs):
        super(PicSpider, self).__init__(*args, **kwargs)
        self.conn = sqlite3.connect(get_project_settings().get(
            "DATABASE_PATH", 'downloads/data.db'))
        self.start = start if is_number(start) and int(start) > 0 else None
        self.length = int(length) if is_number(length) else -1

    def start_requests(self):
        if self.start is None:
            url = 'http://jandan.net/pic'
        else:
            url = 'http://jandan.net/pic/page-' + str(self.start)
        request = scrapy.Request(url, self.parse, headers={
                                 "Host": "jandan.net"})
        request.meta['PhantomJS'] = True
        yield request

    def parse(self, response):
        self.view_page(response.url)
        print(self.length, response.url)
        self.length -= 1
        for sel in response.xpath('//li[starts-with(@id, "comment-")]'):
            commentItem = CommentItem()
            commentItem['id'] = sel.css('.righttext > a::text').extract()
            commentItem['author'] = sel.css('.author > strong::text').extract()

            content = []
            nodes = [s.root for s in sel.css('.text > p').xpath('node()')]
            i = 0
            while i < len(nodes):
                node = nodes[i]
                if hasattr(node, 'tag'):
                    tag = node.tag.lower()
                if isinstance(node, str):
                    item = TextItem(text=node)
                elif tag == 'br':
                    item = BrItem()
                elif tag == 'a':
                    if node.text == '[查看原图]' and \
                            i + 2 < len(nodes) and \
                            nodes[i + 1].tag.lower() == 'br' and \
                            nodes[i + 2].tag.lower() == 'img':
                        item = ImageItem(uri=urljoin(response.url, node.attrib['href']),
                                         alt=nodes[i + 2].attrib.get('alt') or '')
                        i += 2
                    else:
                        item = LinkItem(
                            url=node.attrib['href'], text=node.text)
                elif tag == 'img':
                    item = ImageItem(
                        uri=urljoin(response.url, node.attrib['src']), alt=node.attrib.get('alt') or '')
                else:
                    item = TextItem(text=node.text)
                content.append(item)
                i += 1

            commentItem['content'] = content
            yield commentItem

        next_url = response.css(
            '.previous-comment-page').xpath('@href').extract()[0]
        next_url = urljoin(response.url, next_url)
        if self.length > 0:
            request = scrapy.Request(next_url, self.parse,
                                     headers={"Host": "jandan.net",
                                              "Referer": response.url, }
                                     )
        elif self.length < 0 and not self.has_crawled(next_url):
            request = scrapy.Request(next_url, self.parse,
                                     headers={"Host": "jandan.net",
                                              "Referer": response.url, }
                                     )
        else:
            return
        request.meta['PhantomJS'] = True
        yield request

    def has_crawled(self, page):
        match = re.match('http://jandan.net/pic/page-(\\d+)', page)
        if not match:
            return False
        index = int(match.group(1))
        cur = self.conn.execute(
            'SELECT * FROM `viewed-pages` WHERE `page` = ?', (index,))
        if get_project_settings().get("INCREASE_MODE", True):
            return cur.fetchone() is not None
        else:
            return False

    def view_page(self, page):
        match = re.match('http://jandan.net/pic/page-(\\d+)', page)
        if not match:
            return
        index = int(match.group(1))
        cur = self.conn.execute(
            'SELECT * FROM `viewed-pages` WHERE `page` = ?', (index,))
        if cur.fetchone() is not None:
            return # already crawled
        self.conn.execute(
            'INSERT INTO `viewed-pages`(`page`) VALUES (?);', (index,))
        self.conn.commit()
