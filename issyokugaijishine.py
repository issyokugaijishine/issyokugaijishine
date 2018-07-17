#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re
import time
import datetime
from urllib import parse
from bs4 import BeautifulSoup


class Issyokugaijishine:
    def __init__(self):
        class Gaiji:
            def __init__(self):
                self._ids = set([])
                self.urls = set([])

            def attack(self, url):
                pass

        self.gaiji = Gaiji()
        self._ids = set([])
        self.bname = None
        self.burl = None

    def boards(self):
        url = 'https://menu.5ch.net/bbstable.html'
        r = requests.get(url)
        text = r.content.decode("shift-jis", "ignore")
        document = BeautifulSoup(text, "lxml")
        for a in document.select("a"):
            yield a.text.strip(), a.get("href")

    def check_index(self, url, suffix):
        res = set([])
        r = requests.get(url)
        text = r.content.decode("shift-jis", "ignore")
        document = BeautifulSoup(text, "lxml")
        for dt in document.select("dt"):
            s = 'ID:([a-zA-Z0-9]{8}'
            s += suffix
            s += ')'
            s = re.compile(s)
            s = re.search(s, dt.text)
            if s:
                _id = s.group(0)
                self._ids.add(_id)
                title = dt.parent.parent.find(class_="thread_title")
                title = title.text.strip()
                hrefs = dt.parent.parent.findAll("a")
                hrefs = [
                    x for x in hrefs
                    if x.get("href").find('/test/read.cgi') == 0
                ]
                href = hrefs[0].get("href")
                url = parse.urljoin(url, href)
                res.add((title, url))
        for title, url in res:
            yield title, url

    def check_permalink(self, url):
        url += "1-10n"
        r = requests.get(url)
        text = r.content.decode("shift-jis", "ignore")
        res = False
        for _id in self._ids:
            if text.find(_id) > 0:
                # 対象の末尾が建てたスレッド
                document = BeautifulSoup(text, "lxml")
                _ids = [x.text.strip()
                        for x in document.findAll("span", class_="uid")]
                posts = document.findAll(class_="post")
                if len(_ids) < len(posts):
                    # ID消し野郎が居たら一食ガイジスレ判定
                    res = _id
        return res

    def service(self, bname="なんでも実況J", suffix="H", interval=60):
        while 1:
            if not self.bname and not self.burl:
                self.bname, self.burl = [
                    x for x in self.boards() if x[0] == bname][0]
            for title, url in self.check_index(self.burl, suffix):
                _id = self.check_permalink(url)
                if _id:
                    self.gaiji._ids.add(_id)
                    self.gaiji.urls.add((title, url, True))
            print(datetime.datetime.now())
            print("監視対象板", self.bname)
            print("監視対象末尾", suffix)
            print("監視間隔(sec)", interval)
            print("ガイジID", self.gaiji._ids)
            print("ガイジURL", self.gaiji.urls)
            print()
            for url in self.gaiji.urls:
                self.gaiji.attack(url)
            time.sleep(interval)
