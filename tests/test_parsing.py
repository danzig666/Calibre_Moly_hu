#!/usr/bin/env python
from __future__ import print_function

import importlib.util
import os
import sys


PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGE_NAME = 'calibre_plugins.moly_hu'


def load_plugin_package():
    spec = importlib.util.spec_from_file_location(
        PACKAGE_NAME, os.path.join(PLUGIN_DIR, '__init__.py'),
        submodule_search_locations=[PLUGIN_DIR])
    module = importlib.util.module_from_spec(spec)
    sys.modules[PACKAGE_NAME] = module
    spec.loader.exec_module(module)
    return module


plugin_module = load_plugin_package()
from calibre_plugins.moly_hu.html_utils import parse_html
from calibre_plugins.moly_hu.worker import Worker


class Log(object):
    def info(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def exception(self, *args, **kwargs):
        pass


class SearchHarness(object):
    prefs = {plugin_module.Moly_hu.KEY_MAX_BOOKS: 3}
    normalize_for_match = plugin_module.Moly_hu.normalize_for_match


DETAIL_HTML = b'''<!doctype html>
<html><head><meta charset="utf-8"></head><body>
<div id="content">
  <div class="head"><div class="head_title">
    <div class="authors"><a>B\xc3\xa1lint \xc3\x81gnes</a></div>
    <h1><span class="item">Haj\xc3\xb3\xe2\x80\x8bnapl\xc3\xb3
      <a href="/sorozatok/szeleburdi-csalad">(Szeleburdi csal\xc3\xa1d 2.)</a>
    </span><span class="rating"><span class="like_count">94%</span></span></h1>
  </div></div>
  <div class="coverbox"><a class="zoom" href="/system/covers/big/one.jpg"></a>
    <a rel="modal" href="/boritok/1/view">not a cover</a></div>
  <div class="text shrinkable"><p>Els\xc5\x91 mondat.<br>M\xc3\xa1sodik mondat.</p></div>
  <div id="book_tags"><a class="tag">magyar nyelv\xc5\xb1</a><a class="tag genre">reg\xc3\xa9ny</a></div>
  <div class="items"><div class="edition edition_1">
    <div><a href="/kiadok/mora">M\xc3\xb3ra</a>, <abbr>2020</abbr></div>
    <div><strong>ISBN</strong>: 9786150254036</div>
  </div></div>
</div></body></html>'''


SEARCH_HTML = b'''<html><body><div id="content">
<div class="search_area"><p>
  <a class="book_selector extra" href="/konyvek/balint-agnes-hajonaplo">
    B\xc3\xa1lint \xc3\x81gnes: <strong>Haj\xc3\xb3napl\xc3\xb3</strong>
  </a>
  <a class="book_selector" href="/konyvek/mas-valaki-mas-konyv">
    M\xc3\xa1s Valaki: M\xc3\xa1s k\xc3\xb6nyv
  </a>
</p></div></div></body></html>'''


def test_detail_parsers():
    root = parse_html(DETAIL_HTML)
    worker = object.__new__(Worker)
    worker.log = Log()
    worker.max_covers = 5

    assert worker.parse_title(root) == 'Haj\u00f3napl\u00f3'
    assert worker.parse_authors(root) == ['B\u00e1lint \u00c1gnes']
    assert worker.parse_series(root) == ('Szeleburdi csal\u00e1d', '2')
    assert worker.parse_isbn(root) == '9786150254036'
    assert worker.parse_publisher(root) == 'M\u00f3ra'
    assert worker.parse_published_date(root).year == 2020
    assert worker.parse_tags(root) == ['magyar nyelv\u0171', 'reg\u00e9ny']
    assert worker.parse_languages(worker.parse_tags(root)) == ['hu']
    assert worker.parse_rating(root) == 9.4
    assert worker.parse_comments(root) == 'Els\u0151 mondat.\nM\u00e1sodik mondat.'
    assert worker.parse_covers(root) == [
        'https://moly.hu/system/covers/big/one.jpg']


def test_search_is_scoped_and_filtered():
    harness = SearchHarness()
    root = parse_html(SEARCH_HTML)
    matches = []
    plugin_module.Moly_hu._parse_search_results(
        harness, Log(), 'Haj\u00f3napl\u00f3', ['\u00c1gnes B\u00e1lint'], root,
        matches, 30, None)
    assert matches == ['https://moly.hu/konyvek/balint-agnes-hajonaplo']

    homepage = parse_html(
        b'<div id="content"><a class="book_selector" '
        b'href="/konyvek/random">Random Author: Random Book</a></div>')
    matches = []
    plugin_module.Moly_hu._parse_search_results(
        harness, Log(), 'Haj\u00f3napl\u00f3', None, homepage, matches, 30, None)
    assert matches == []


def test_current_query_parameter():
    query = plugin_module.Moly_hu.create_query(
        SearchHarness(), Log(), 'Haj\u00f3napl\u00f3', ['B\u00e1lint \u00c1gnes'], {})
    assert query.startswith('https://moly.hu/kereses?query=')
    assert '&q=' not in query


if __name__ == '__main__':
    test_detail_parsers()
    test_search_is_scoped_and_filtered()
    test_current_query_parameter()
    print('All parser tests passed')
