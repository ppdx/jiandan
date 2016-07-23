# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

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
        self.conn = sqlite3.connect(jiandan.settings.DATABASE_PATH)
        cursor = self.conn.cursor()
        cursor.execute(
            '''select count(*) from sqlite_master where type='table' and name='data' ''')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
CREATE TABLE `data` (
    `id`    INTEGER NOT NULL UNIQUE,
    `author`    TEXT NOT NULL,
    `content`   TEXT NOT NULL,
    PRIMARY KEY(id)
)''')
        cursor.close()
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        item['id'] = tostring(item['id'])
        item['author'] = tostring(item['author'])
        if item['id'] == '' or item['author'] == '':
            raise DropItem('id or author is empty!')
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT count(*) FROM `data` WHERE `id`=?', (int(item['id']),))
            if cursor.fetchone()[0] != 0:
                raise DropItem('item already exist!')
        except ValueError:
            raise DropItem('id cannot convert to int!')
        finally:
            cursor.close()
        return item


class PicImagesPipeline(ImagesPipeline):

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
        self.conn = sqlite3.connect(jiandan.settings.DATABASE_PATH)
        cursor = self.conn.cursor()
        cursor.execute(
            '''select count(*) from sqlite_master where type='table' and name='data' ''')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
CREATE TABLE `data` (
    `id`    INTEGER NOT NULL UNIQUE,
    `author`    TEXT NOT NULL,
    `content`   TEXT NOT NULL,
    PRIMARY KEY(id)
)''')
        cursor.close()
        self.conn.commit()

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
            root, encoding='utf-8', pretty_print=True)
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO `data`(`id`,`author`,`content`) VALUES (?,?,?)',
            (item['id'], item['author'], item['content']))
        cursor.close()
        self.conn.commit()
        return item
