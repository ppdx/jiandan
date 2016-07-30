#! python3
# -*- coding: utf-8 -*-

from lxml import etree
import sqlite3
import json
from os.path import split
from collections import defaultdict

DB = '../downloads/data.db'
MAPPING = 'mapping.json'
URL_FILE = 'url.txt'

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("select * from data where content like '%http%'")  # 具有未下载图片链接的
all = cur.fetchall()
cur.close()
conn.close()

mapping = defaultdict(list)
urls = set()

for item in all:
    node = etree.fromstring(item[2])
    childs = node.xpath('*')
    for child in childs:
        if child.tag == 'img' and child.get('src', '').startswith('http'):
            src = child.get('src')
            urls.add(src)
            name = split(src)[1]
            mapping[name].append(item[0])

with open(URL_FILE, 'w') as f:
    for url in urls:
        print(url, file=f)
json.dump(mapping, open(MAPPING, 'w'), indent=2)
