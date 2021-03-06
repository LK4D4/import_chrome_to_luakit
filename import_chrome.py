#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sqlite3
import time

from collections import namedtuple
from HTMLParser import HTMLParser

Bookmark = namedtuple('LuakitBook', ['uri', 'title', 'desc', 'tags', 'created', 'modified'])


class ChromeBookParser(HTMLParser):

    def __init__(self, chrome_html_bookmarks):
        HTMLParser.__init__(self)
        self.curr_time = time.time()
        self.current_tag = ("", {})
        self.bookmarks = []
        self.current_dir = ""
        self.feed(chrome_html_bookmarks)

    def handle_starttag(self, tag, attrs):
        if tag != "dt" and tag != "p":
            self.current_tag = (tag, dict(attrs))

    def handle_endtag(self, tag):
        self.current_tag = ("", {})
        if tag == "dl":
            self.current_dir = ""

    def handle_data(self, data):
        tag, attrs = self.current_tag
        if tag == "h3" and attrs.get("personal_toolbar_folder") != "true":
            self.current_dir = unicode(data, 'utf8')
        elif tag == "a":
            self.bookmarks.append(
                Bookmark(attrs["href"], unicode(data, 'utf8'), "",
                         self.current_dir, self.curr_time, self.curr_time)
            )


def load_to_luakit(chrome_books, luakit_db):
    """Load chrome bookmarks to luakit bookmarks sqlite db.
    :params chrome_books: chrome bookmarks in special data structure
    :type chrome_books: list of LuakitBook
    :params luakit_db: sqlite database of luakit bookmarks
    :type luakit_db: string
    """
    conn = sqlite3.connect(luakit_db)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS bookmarks (
                        id INTEGER PRIMARY KEY,
                        uri TEXT NOT NULL,
                        title TEXT NOT NULL,
                        desc TEXT NOT NULL,
                        tags TEXT NOT NULL,
                        created INTEGER,
                        modified INTEGER
                      );""")

    cursor.executemany("INSERT INTO bookmarks VALUES (NULL, ?, ?, ?, ?, ?, ?)", chrome_books)
    conn.commit()
    conn.close()


def main(args):
    chrome_parser = ChromeBookParser(open(args.chrome_books).read())
    chrome_books = chrome_parser.bookmarks
    load_to_luakit(chrome_books, args.luakit_books)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import Chrome bookmarks to luakit bookmarks db.')
    parser.add_argument('chrome_books', help="Chrome bookmarks in html format")
    parser.add_argument('luakit_books', help="Luakit bookmarks in sqlite format")
    args = parser.parse_args()
    main(args)
