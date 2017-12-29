# -*- coding: utf-8 -*-
import sqlite3

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os

if not os.path.exists("downloads"):
    os.mkdir("downloads")

settings = get_project_settings()

conn = sqlite3.connect(settings["DATABASE_PATH"])
conn.executescript(open("create table.sql").read())
conn.close()

process = CrawlerProcess(settings)

# 'followall' is the name of one of the spiders of the project.
process.crawl('pic')
process.start()  # the script will block here until the crawling is finished
