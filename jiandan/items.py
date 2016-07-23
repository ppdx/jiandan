# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CommentItem(scrapy.Item):
    id = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()


class TextItem(scrapy.Item):
    text = scrapy.Field()


class ImageItem(scrapy.Item):
    uri = scrapy.Field()
    alt = scrapy.Field()


class LinkItem(scrapy.Item):
    url = scrapy.Field()
    text = scrapy.Field()


class BrItem(scrapy.Item):
    pass
