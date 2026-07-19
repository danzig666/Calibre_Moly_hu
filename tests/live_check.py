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
print('Live identify passed:', found[0])
print('Live cover download passed')
