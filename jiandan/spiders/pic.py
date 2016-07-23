# -*- coding: utf-8 -*-
import scrapy
from jiandan.items import *


class PicSpider(scrapy.Spider):
    name = "pic"
    allowed_domains = ["jandan.net/"]
    start_urls = (
        # 'http://www.jandan.net/pic/',
        'http://jandan.net/pic/page-9389',
    )

    def __init__(self, min=-1, max=-1, len=-1, *args, **kwargs):
        super(PicSpider, self).__init__(*args, **kwargs)

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
