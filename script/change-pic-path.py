#! python3
# -*- coding: utf-8 -*-

import sqlite3
import re

DB = '../downloads/data.db'

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("select * from data")
all = cur.fetchall()

for (id, author, content) in all:
    content = re.sub('src=([^"])', r'src="image/\1', content)
    cur.execute('UPDATE data SET content = ? WHERE id = ?', (content, id))

cur.close()
conn.commit()
conn.close()
