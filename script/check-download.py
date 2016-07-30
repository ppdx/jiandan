#! python3
# -*- coding: utf-8 -*-

import sqlite3
from lxml import etree
from os.path import split, join, exists

URLFILE = '../downloads/url.txt'
IMAGE_PATH = '../downloads/image/'
DOWNLOADS_PATH = '../downloads'
DB = '../downloads/data.db'

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("select * from data")
all = cur.fetchall()

for (id, author, content) in all:
    node = etree.fromstring(content)
    childs = node.xpath('*')
    for child in childs:
        if child.tag == 'img' and child.get('src', '').startswith('http'):
            src = child.get('src')
            if not exists(join(DOWNLOADS_PATH,split(src)[1])):
                print(id)

cur.close()
conn.commit()
conn.close()
