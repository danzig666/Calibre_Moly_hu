#!/usr/bin/env python
# vim:fileencoding=utf-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

from calibre.utils.cleantext import clean_ascii_chars
from lxml.html import HTMLParser, fromstring


def parse_html(raw):
    """Parse a UTF-8 Moly response using lxml's tolerant byte parser.

    Passing decoded Moly pages directly to ``fromstring`` can make some lxml
    versions fail with ``XMLSyntaxError: internal error``.  Cleaning as text
    and then parsing UTF-8 bytes avoids that code path and also lets the HTML
    parser recover from imperfect markup on the site.
    """
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8', errors='replace')
    raw = clean_ascii_chars(raw)
    parser = HTMLParser(encoding='utf-8', recover=True)
    return fromstring(raw.encode('utf-8'), parser=parser)
