#!/usr/bin/env python
# vim:fileencoding=utf-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
import unicodedata
from calibre import browser
from calibre.ebooks.metadata.sources.base import Source, Option
from calibre.ebooks.metadata import check_isbn
from calibre import as_unicode
from calibre_plugins.moly_hu.html_utils import parse_html
import sys
import time

__license__ = 'GPL v3'
__copyright__ = '2011-2018, Hoffer Csaba <csaba.hoffer@gmail.com>, Kloon <kloon@techgeek.co.in>, otapi <otapigems.com>, Dezso <orai.dezso@gmail.com>'
__docformat__ = 'restructuredtext hu'


is_py2 = sys.version[0] == '2'
if is_py2:
    from Queue import Queue, Empty
    from urllib import quote
else:
    from queue import Queue, Empty
    from urllib.parse import quote


class Moly_hu(Source):
    name = 'Moly_hu'
    description = _('Downloads metadata and covers from moly.hu')
    author = 'Hoffer Csaba & Kloon & fatsadt & otapi & Dezso'
    version = (1, 1, 0)
    minimum_calibre_version = (0, 8, 0)

    capabilities = frozenset(['identify', 'cover'])
    touched_fields = frozenset(['title', 'authors', 'identifier:isbn', 'identifier:moly_hu', 'tags',
                                'comments', 'rating', 'series', 'series_index', 'publisher', 'pubdate', 'language', 'languages'])
    has_html_comments = False
    supports_gzip_transfer_encoding = False
    can_get_multiple_covers = True

    KEY_MAX_BOOKS = 'max_books'
    KEY_MAX_COVERS = 'max_covers'

    options = (Option(KEY_MAX_BOOKS, 'number', 3, _('Maximum number of books to get'),
                      _('The maximum number of books to process from the moly.hu search result')),
               Option(KEY_MAX_COVERS, 'number', 5, _('Maximum number of covers to get'),
                      _('The maximum number of covers to process for the chosen book'))
               )

    BASE_URL = 'https://moly.hu'
    BOOK_URL = BASE_URL + '/konyvek/'
    SEARCH_URL = BASE_URL + '/kereses?query='

    def create_query(self, log, title=None, authors=None, identifiers={}):
        isbn = check_isbn(identifiers.get('isbn', None))
        if isbn is not None:
            return Moly_hu.SEARCH_URL + isbn
        terms = []
        if authors:
            terms.append(authors[0])
        if title:
            terms.append(title)
        if not terms:
            return None
        query = ' '.join(terms)
        return Moly_hu.SEARCH_URL + quote(query.encode('utf-8'))

    def get_cached_cover_url(self, identifiers):
        url = None
        moly_id = identifiers.get('moly_hu', None)
        if moly_id is None:
            isbn = check_isbn(identifiers.get('isbn', None))
            if isbn is not None:
                moly_id = self.cached_isbn_to_identifier(isbn)
        if moly_id is not None:
            url = self.cached_identifier_to_cover_url(moly_id)
        return url

    def identify(self, log, result_queue, abort, title, authors,
                 identifiers={}, timeout=30):
        '''
        Note this method will retry without identifiers automatically if no
        match is found with identifiers.
        '''
        matches = []
        moly_id = identifiers.get('moly_hu', None)
        isbn = check_isbn(identifiers.get('isbn', None))
        log.info(u'\nTitle:%s\nAuthors:%s\n' % (title, authors))
        br = browser()
        if moly_id:
            matches.append(Moly_hu.BOOK_URL + moly_id)
        else:
            query = self.create_query(
                log, title=title, authors=authors, identifiers=identifiers)
            if query is None:
                log.error('Insufficient metadata to construct query')
                return
            try:
                log.info('Querying: %s' % query)
                response = br.open(query, timeout=timeout)
            except Exception as e:
                if callable(getattr(e, 'getcode', None)) and e.getcode() == 404:
                    log.info('Failed to find match for ISBN: %s' % isbn)
                else:
                    err = 'Failed to make identify query: %r' % query
                    log.exception(err)
                    return as_unicode(e)

            try:
                raw = response.read().strip()
                if not raw:
                    log.error('Failed to get raw result for query: %r' % query)
                    return
                root = parse_html(raw)
            except:
                msg = 'Failed to parse moly.hu page for query: %r' % query
                log.exception(msg)
                return msg
            self._parse_search_results(
                log, title, authors, root, matches, timeout, isbn)

        if abort.is_set():
            return

        if not matches:
            log.error('No matches found with query: %r' % query)
            if identifiers and title and authors:
                log.info('No matches found with identifiers, retrying using only'
                         ' title and authors')
                return self.identify(log, result_queue, abort, title=title,
                                     authors=authors, timeout=timeout)
            elif title and authors and title != title.split("(")[0]:
                log.info(
                    'No matches found with authors and title try removing () part from title, and search by title and author')
                tit = title.split("(")[0]
                return self.identify(log, result_queue, abort, title=tit,
                                     authors=authors, timeout=timeout)
            elif title and authors:
                log.info(
                    'No matches found with authors and title, retrying using only title')
                return self.identify(log, result_queue, abort, title=title,
                                     authors=None, timeout=timeout)
            return

        from calibre_plugins.moly_hu.worker import Worker
        workers = [Worker(url, result_queue, br, log, i, self) for i, url in
                   enumerate(matches)]

        for w in workers:
            w.start()
            time.sleep(0.1)

        while not abort.is_set():
            a_worker_is_alive = False
            for w in workers:
                w.join(0.2)
                if abort.is_set():
                    break
                if w.is_alive():
                    a_worker_is_alive = True
            if not a_worker_is_alive:
                break

        return None

    def _parse_search_results(self, log, orig_title, orig_authors, root, matches, timeout, isbn):
        max_results = self.prefs[Moly_hu.KEY_MAX_BOOKS]
        results = root.xpath(
            '//*[@id="content"]'
            '//div[contains(concat(" ", normalize-space(@class), " "), '
            '" search_area ")]'
            '//a[contains(concat(" ", normalize-space(@class), " "), '
            '" book_selector ")]')
        log.info('Found %d possible books (max: %d)' %
                 (len(results), max_results))
        i = 0
        for result in results:
            book_urls = result.xpath('@href')

            if isbn is None:
                author_n_title = ''.join(result.itertext())
                author_n_titles = author_n_title.split(':', 1)
                if len(author_n_titles) != 2:
                    continue
                author = author_n_titles[0].strip()
                title = author_n_titles[1].strip()
                log.info('Orig: %s, target: %s' % (
                    self.normalize_for_match(orig_title),
                    self.normalize_for_match(title)))

                if orig_title:
                    if (self.normalize_for_match(orig_title) not in
                            self.normalize_for_match(title)):
                        continue
                if orig_authors:
                    author1 = orig_authors[0]
                    author_parts = author1.split()
                    author2 = ' '.join(reversed(author_parts))
                    normalized_author = self.normalize_for_match(author)
                    if (self.normalize_for_match(author1) not in normalized_author
                            and self.normalize_for_match(author2) not in
                            normalized_author):
                        continue

            for book_url in book_urls:
                result_url = Moly_hu.BASE_URL + book_url

                if (result_url not in matches):
                    matches.append(result_url)
                    i += 1
                if (i >= max_results):
                    return
        # Do not fall back to arbitrary book links.  Moly redirects obsolete or
        # malformed searches to its home page, which contains unrelated books.

    def strip_accents(self, s):
        return self.normalize_for_match(s)

    def normalize_for_match(self, value):
        if value is None:
            return None
        value = unicodedata.normalize('NFKD', value)
        value = ''.join(char for char in value
                        if not unicodedata.combining(char))
        value = ''.join(char if char.isalnum() else ' ' for char in value)
        return ' '.join(value.lower().split())

    def download_cover(self, log, result_queue, abort, title=None, authors=None, identifiers={}, timeout=30, get_best_cover=False):
        if not title:
            return
        urls = self.get_image_urls(
            title, authors, identifiers, log, abort, timeout)
        self.download_multiple_covers(
            title, authors, urls, get_best_cover, timeout, result_queue, abort, log)

    def get_image_urls(self, title, authors, identifiers, log, abort, timeout):
        cached_url = self.get_cached_cover_url(identifiers)
        if cached_url is None:
            log.info('No cached cover found, running identify')
            rq = Queue()
            self.identify(log, rq, abort, title=title,
                          authors=authors, identifiers=identifiers)
            if abort.is_set():
                return
            results = []
            while True:
                try:
                    results.append(rq.get_nowait())
                except Empty:
                    break
            results.sort(key=self.identify_results_keygen(
                title=title, authors=authors, identifiers=identifiers))
            for mi in results:
                cached_url = self.get_cached_cover_url(mi.identifiers)
                if cached_url is not None:
                    break

        if cached_url is not None:
            return cached_url

        log.info('No cover found')
        return []
