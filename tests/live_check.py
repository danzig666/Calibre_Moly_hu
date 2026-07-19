#!/usr/bin/env python
from __future__ import print_function

import os
import runpy
import sys
import threading
import traceback

try:
    from queue import Queue, Empty
except ImportError:
    from Queue import Queue, Empty


HERE = os.path.dirname(os.path.abspath(__file__))
test_module = runpy.run_path(os.path.join(HERE, 'test_parsing.py'))
plugin_module = test_module['plugin_module']


class ConsoleLog(object):
    def __call__(self, message):
        self.info(message)

    def info(self, message):
        print('INFO:', message)

    def error(self, message):
        print('ERROR:', message, file=sys.stderr)

    def exception(self, message):
        print('ERROR:', message, file=sys.stderr)
        traceback.print_exc()


plugin = plugin_module.Moly_hu(None)
plugin.prefs[plugin.KEY_MAX_BOOKS] = 3
plugin.prefs[plugin.KEY_MAX_COVERS] = 5
results = Queue()
plugin.identify(
    ConsoleLog(), results, threading.Event(), title='Haj\u00f3napl\u00f3',
    authors=['B\u00e1lint \u00c1gnes'], identifiers={}, timeout=30)

found = []
while True:
    try:
        found.append(results.get_nowait())
    except Empty:
        break

assert found, 'Live identify returned no results'
assert found[0].title == 'Haj\u00f3napl\u00f3', found[0].title
assert 'B\u00e1lint \u00c1gnes' in found[0].authors, found[0].authors
assert found[0].get_identifier('moly_hu') == 'balint-agnes-hajonaplo'
cover_results = Queue()
plugin.download_cover(
    ConsoleLog(), cover_results, threading.Event(), title=found[0].title,
    authors=found[0].authors, identifiers=found[0].identifiers, timeout=30,
    get_best_cover=True)
assert not cover_results.empty(), 'Live cover download returned no data'

# Regression check for the page that triggered lxml's Unicode parser error.
regression_results = Queue()
plugin.identify(
    ConsoleLog(), regression_results, threading.Event(),
    title='Egy cs\u00fanya n\u0151', authors=['\u00c1kody Zsuzsa'],
    identifiers={'moly_hu': 'akody-zsuzsa-egy-csunya-no'}, timeout=30)
regression = regression_results.get_nowait()
assert regression.title == 'Egy cs\u00fanya n\u0151', regression.title
assert regression.get_identifier('moly_hu') == 'akody-zsuzsa-egy-csunya-no'

# Moly separates this Calibre title into a short title and a series link.
series_results = Queue()
plugin.identify(
    ConsoleLog(), series_results, threading.Event(),
    title='Egy Zizi napl\u00f3ja: Popszt\u00e1r',
    authors=['Rachel Renee Russell'], identifiers={}, timeout=30)
series_book = series_results.get_nowait()
assert series_book.title == 'Popszt\u00e1r', series_book.title
assert series_book.series == 'Egy Zizi napl\u00f3ja', series_book.series
assert series_book.series_index == 3, series_book.series_index
series_covers = Queue()
plugin.download_cover(
    ConsoleLog(), series_covers, threading.Event(),
    title='Egy Zizi napl\u00f3ja: Popszt\u00e1r',
    authors=['Rachel Renee Russell'], identifiers={}, timeout=30,
    get_best_cover=True)
assert not series_covers.empty(), 'Series-prefixed title returned no cover'
print('Live identify passed:', found[0])
print('Live cover download passed')
print('lxml regression page passed:', regression.title)
print('Series-prefixed title and cover passed:', series_book.title)
