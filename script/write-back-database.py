#! python3
# -*- coding: utf-8 -*-

import sqlite3
from lxml import etree
from os.path import split, join

DB = '../downloads/data.db'
MAPPING = 'mapping.json'

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("select * from data where content like '%http%'")
all = cur.fetchall()

for (id, author, content) in all:
    node = etree.fromstring(content)
    childs = node.xpath('*')
    for child in childs:
        if child.tag == 'img' and child.get('src', '').startswith('http'):
            src = child.get('src')
            child.set('src', join('image', split(src)[1]))
    cur.execute('UPDATE data SET content = ? WHERE id = ?',
                (etree.tostring(node, encoding='unicode'), id))

cur.close()
conn.commit()
conn.close()
