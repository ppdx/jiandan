# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.utils.project import get_project_settings

import jiandan
from jiandan.items import *
from lxml import etree
from os import path
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import sqlite3


def tostring(x):
    if isinstance(x, str):
        return x
    if isinstance(x, (list, tuple)):
        return ' '.join(x).strip()


class RemovePipeline:

    def open_spider(self, spider):
        self.conn = sqlite3.connect(get_project_settings().get("DATABASE_PATH", 'downloads/data.db'))

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        item['id'] = tostring(item['id'])
        item['author'] = tostring(item['author'])
        if item['id'] == '' or item['author'] == '':
            raise DropItem('id or author is empty!')
        try:
            cursor = self.conn.execute(
                'SELECT count(*) FROM `data` WHERE `id`=?', (int(item['id']),))
            if cursor.fetchone()[0] != 0:
                raise DropItem('item already exist!')
        except ValueError:
            raise DropItem('id cannot convert to int!')
        return item


class PicImagesPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        return path.split(request.url)[1]

    def get_media_requests(self, item, info):
        for i in item['content']:
            if isinstance(i, ImageItem):
                yield scrapy.Request(i['uri'])

    def item_completed(self, results, item, info):
        d = {it['uri']: i for (i, it) in enumerate(item['content'])
             if isinstance(it, ImageItem)}
        for ok, x in results:
            if ok:
                item['content'][d[x['url']]]['uri'] = path.join(
                    'image', x['path'])
        return item


class StorePipeline:

    def open_spider(self, spider):
        self.conn = sqlite3.connect(get_project_settings().get("DATABASE_PATH", 'downloads/data.db'))

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        root = etree.Element('div')
        root.set('id', item['id'])
        root.set('author', item['author'])
        last_node = None
        for i in item['content']:
            if isinstance(i, TextItem):
                if last_node is not None:
                    last_node.tail = i['text']
                else:
                    root.text = i['text']
            elif isinstance(i, ImageItem):
                last_node = etree.SubElement(root, 'img')
                last_node.set('src', i['uri'])
                if i['alt']:
                    last_node.set('alt', i['alt'])
            elif isinstance(i, LinkItem):
                last_node = etree.SubElement(root, 'a')
                last_node.set('href', i['url'])
                if i['text']:
                    last_node.text = i['text']
            elif isinstance(i, BrItem):
                last_node = etree.SubElement(root, 'br')
        item['content'] = etree.tostring(
            root, encoding='unicode', pretty_print=True).replace(
            '因不受欢迎已被超载鸡自动隐藏.  <a href="javascript:;">[手贱一回]</a>',
            '')

        self.conn.execute(
            'INSERT INTO `data`(`id`,`author`,`content`) VALUES (?,?,?)',
            (item['id'], item['author'], item['content']))
        self.conn.commit()
        return item
