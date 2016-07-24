# -*- coding: utf-8 -*-
import re
import sqlite3
import scrapy
import jiandan
from jiandan.items import *


class PicSpider(scrapy.Spider):
    name = "pic"
    allowed_domains = ["jandan.net"]
    start_urls = (
        'http://jandan.net/pic',
    )

    def __init__(self, start=None, length=None, *args, **kwargs):
        super(PicSpider, self).__init__(*args, **kwargs)
        self.conn = sqlite3.connect(jiandan.settings.DATABASE_PATH)
        cursor = self.conn.cursor()
        cursor.execute(
            '''select count(*) from sqlite_master where type='table' and name='viewed-pages' ''')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
CREATE TABLE `viewed-pages` (
	`page`	INTEGER NOT NULL UNIQUE,
	PRIMARY KEY(page)
)''')
        cursor.close()
        self.conn.commit()
        if start is not None:
            start_urls = ('http://jandan.net/pic/page-' + start,)
        self.length = int(length) if length is not None else -1

    def parse(self, response):
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
                    if node.text == '[查看原图]' and i + 2 < len(nodes) and nodes[i + 1].tag.lower() == 'br' and nodes[i + 2].tag.lower() == 'img':
                        item = ImageItem(uri=node.attrib['href'],
                                         alt=nodes[i + 2].attrib.get('alt') or '')
                        i += 2
                    else:
                        item = LinkItem(
                            url=node.attrib['href'], text=node.text)
                elif tag == 'img':
                    item = ImageItem(
                        uri=node.attrib['href'], alt=node.attrib.get('alt') or '')
                else:
                    item = TextItem(text=node.text)
                content.append(item)
                i += 1

            commentItem['content'] = content
            yield commentItem

        next_url = response.css(
            '.previous-comment-page').xpath('@href').extract()[0]
        if self.length > 1:
            self.length -= 1
            self.view_page(next_url)
            yield scrapy.Request(next_url, self.parse)
        elif self.length < 0 and not self.has_crawled(next_url):
            self.view_page(next_url)
            yield scrapy.Request(next_url, self.parse)

    def has_crawled(self, page):
        match = re.match('http://jandan.net/pic/page-(\\d+)', page)
        if not match:
            return False
        index = int(match.group(1))
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                '''SELECT * FROM `viewed-pages` WHERE `page` = ?''', (index,))
            if cursor.fetchone() is not None:
                cursor.execute(
                    'INSERT INTO `viewed-pages`(`page`) VALUES (?);', (index,))
                return True
            return False
        finally:
            cursor.close()

    def view_page(self, page):
        match = re.match('http://jandan.net/pic/page-(\\d+)', page)
        if not match:
            return
        index = int(match.group(1))
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO `viewed-pages`(`page`) VALUES (?);', (index,))
        except sqlite3.IntegrityError:
            pass
        finally:
            cursor.close()
            self.conn.commit()
