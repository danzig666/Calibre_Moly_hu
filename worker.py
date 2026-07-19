#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)
from calibre.utils.date import utc_tz
from datetime import datetime
from calibre.ebooks.metadata.book.base import Metadata
from calibre.ebooks.metadata import check_isbn
from calibre_plugins.moly_hu.html_utils import parse_html
from threading import Thread

__license__ = 'GPL v3'
__copyright__ = '2011-2014, Hoffer Csaba <csaba.hoffer@gmail.com>, Kloon <kloon@techgeek.co.in>'
__docformat__ = 'restructuredtext hu'

import socket
import re
import sys

is_py2 = sys.version[0] == '2'
if not is_py2:
    unicode = str


class Worker(Thread):  # Get details
    '''
    Get book details from moly.hu book page in a separate thread
    '''

    def __init__(self, url, result_queue, browser, log, relevance, plugin, timeout=30):
        Thread.__init__(self)
        self.daemon = True
        self.url, self.result_queue = url, result_queue
        self.log, self.timeout = log, timeout
        self.relevance, self.plugin = relevance, plugin
        self.browser = browser.clone_browser()
        self.max_covers = plugin.prefs[plugin.KEY_MAX_COVERS]
        self.cover_url = self.moly_id = self.isbn = None

    def run(self):
        try:
            self.get_details()
        except:
            self.log.exception('get_details failed for url: %r' % self.url)

    def get_details(self):
        try:
            raw = self.browser.open_novisit(
                self.url, timeout=self.timeout).read().strip()
            if not raw:
                self.log.error(
                    'Failed to get book details for URL: %r' % self.url)
                return
        except Exception as e:
            if callable(getattr(e, 'getcode', None)) and e.getcode() == 404:
                self.log.error('URL malformed: %r' % self.url)
                return
            attr = getattr(e, 'args', [None])
            attr = attr if attr else [None]
            if isinstance(attr[0], socket.timeout):
                msg = 'Moly.hu timed out. Try again later.'
                self.log.error(msg)
            else:
                msg = 'Failed to make details query: %r' % self.url
                self.log.exception(msg)
            return

        root = parse_html(raw)
        self.parse_details(root)

    def parse_details(self, root):
        try:
            moly_id = self.parse_moly_id(self.url)
            self.log.info('Parsed moly.hu identifier: %s' % moly_id)
        except:
            self.log.exception(
                'Error parsing moly.hu id for url: %r' % self.url)
            moly_id = None

        try:
            title = self.parse_title(root)
            self.log.info('Parsed title: %s' % title)
        except:
            self.log.exception('Error parsing title for url: %r' % self.url)
            title = None

        try:
            authors = self.parse_authors(root)
            self.log.info('Parsed authors: %s' % authors)
        except:
            self.log.exception('Error parsing authors for url: %r' % self.url)
            authors = []

        if not title or not authors or not moly_id:
            self.log.error(
                'Could not find title/authors/moly.hu id for %r' % self.url)
            self.log.error('Moly.hu id: %r Title: %r Authors: %r' %
                           (moly_id, title, authors))
            return

        mi = Metadata(title, authors)
        mi.set_identifier('moly_hu', moly_id)
        self.moly_id = moly_id

        try:
            isbn = self.parse_isbn(root)
            self.log.info('Parsed ISBN: %s' % isbn)
            if isbn:
                self.isbn = mi.isbn = isbn
        except:
            self.log.exception('Error parsing ISBN for url: %r' % self.url)

        try:
            series_info = self.parse_series(root)
            if series_info is not None:
                mi.series = series_info[0]
                mi.series_index = float(series_info[1])
                self.log.info('Parsed series: %s, series index: %f' %
                              (mi.series, mi.series_index))
        except:
            self.log.exception('Error parsing series for url: %r' % self.url)

        try:
            mi.comments = self.parse_comments(root)
            self.log.info('Parsed comments: %s' % mi.comments)
        except:
            self.log.exception('Error parsing comments for url: %r' % self.url)

        try:
            self.cover_url = self.parse_covers(root)
            self.log.info('Parsed URL for cover: %r' % self.cover_url)
            self.plugin.cache_identifier_to_cover_url(
                self.moly_id, self.cover_url)
            mi.has_cover = bool(self.cover_url)
        except:
            self.log.exception('Error parsing cover for url: %r' % self.url)

        try:
            mi.tags = self.parse_tags(root)
            self.log.info('Parsed tags: %s' % mi.tags)
        except:
            self.log.exception('Error parsing tags for url: %r' % self.url)

        try:
            mi.languages = self.parse_languages(mi.tags)
            self.log.info('Parsed languages: %r' % mi.languages)
        except:
            self.log.exception('Error parsing language for url: %r' % self.url)

        try:
            mi.publisher = self.parse_publisher(root)
            self.log.info('Parsed publisher: %s' % mi.publisher)
        except:
            self.log.exception(
                'Error parsing publisher for url: %r' % self.url)

        try:
            mi.pubdate = self.parse_published_date(root)
            self.log.info('Parsed publication date: %s' % mi.pubdate)
        except:
            self.log.exception(
                'Error parsing published date for url: %r' % self.url)

        try:
            mi.rating = self.parse_rating(root)
            self.log.info('Parsed rating: %s\n\n' % mi.rating)
        except:
            self.log.exception('Error parsing tags for url: %r\n\n' % self.url)

        mi.source_relevance = self.relevance

        if self.moly_id and self.isbn:
            self.plugin.cache_isbn_to_identifier(self.isbn, self.moly_id)

        self.plugin.clean_downloaded_metadata(mi)

        self.result_queue.put(mi)

    def parse_moly_id(self, url):
        try:
            m = re.search(r'/konyvek/([^/?#]+)', url)
            if m:
                return m.group(1)
        except:
            return None

    def parse_isbn(self, root):
        edition_nodes = root.xpath(
            '//*[@id="content"]'
            '//div[contains(concat(" ", normalize-space(@class), " "), '
            '" items ")]'
            '//div[contains(concat(" ", normalize-space(@class), " "), '
            '" edition ")]')
        if not edition_nodes:
            edition_nodes = root.xpath(
                '//*[@id="content"]//*[@class="items"]/div')
        for edition in edition_nodes:
            text = ' '.join(edition.itertext())
            for candidate in re.findall(r'(?<!\d)[\d-]{10,17}(?!\d)', text):
                isbn = check_isbn(candidate.replace('-', ''))
                if isbn:
                    return isbn

    def parse_title(self, root):
        title_nodes = root.xpath(
            '//*[@id="content"]'
            '//*[contains(concat(" ", normalize-space(@class), " "), '
            '" head_title ")]//h1'
            '/span[contains(concat(" ", normalize-space(@class), " "), '
            '" item ")]')
        if title_nodes:
            # The series link is nested in this span; only direct text belongs
            # to the book title.
            title = ' '.join(title_nodes[0].xpath('./text()'))
            title = self._clean_text(title)
            self.log.info('Title: %s' % title)
            return title
        title_node = root.xpath(
            '//*[@id="content"]//*[@class="book"]/span[1]/text()')
        self.log.info('Title: %s' % title_node)
        if title_node:
            return self._clean_text(title_node[0])

    def parse_series(self, root):
        series_node = root.xpath(
            '//*[@id="content"]//h1'
            '//a[contains(@href, "/sorozatok/")]/text()')
        if not series_node:
            series_node = root.xpath(
                '//*[@id="content"]//*[@class="book"]/span/a/text()')
        if not series_node:
            return None
        value = self._clean_text(series_node[0]).strip('()')
        match = re.match(r'^(.*?)\s+(\d+(?:[.,]\d+)?)\.?$', value)
        if match:
            return match.group(1), match.group(2).replace(',', '.')

    def parse_authors(self, root):
        author_nodes = root.xpath(
            '//*[@id="content"]'
            '//div[contains(concat(" ", normalize-space(@class), " "), '
            '" authors ")]/a/text()')
        self.log.info('Authors: %r' % author_nodes)
        if author_nodes:
            return [self._clean_text(unicode(author)) for author in author_nodes]

    def parse_tags(self, root):
        tags_node = root.xpath(
            '//*[@id="book_tags"]'
            '//a[contains(concat(" ", normalize-space(@class), " "), '
            '" tag ")]/text()')
        if not tags_node:
            tags_node = root.xpath(
                '//*[@id="tags"]//*[@class="hover_link"]/text()')
        tags_node = [self._clean_text(unicode(text)) for text in tags_node
                     if text.strip()]
        if tags_node:
            return tags_node

    def parse_comments(self, root):
        description_node = root.xpath(
            '//*[@id="content"]//*[@id="full_description"]')
        if not description_node:
            description_node = root.xpath(
                '//*[@id="content"]'
                '/div[contains(concat(" ", normalize-space(@class), " "), '
                '" text ")][1]')
        if description_node:
            parts = [self._clean_text(text)
                     for text in description_node[0].itertext() if text.strip()]
            return '\n'.join(part for part in parts if part)

    def parse_publisher(self, root):
        publisher_node = root.xpath(
            '(//*[@id="content"]'
            '//div[contains(concat(" ", normalize-space(@class), " "), '
            '" edition ")])[1]/div[1]/a[contains(@href, "/kiadok/")]/text()')
        if not publisher_node:
            publisher_node = root.xpath(
                '//*[@id="content"]//*[@class="items"]/div/div[1]/a/text()')
        if publisher_node:
            return self._clean_text(publisher_node[0])

    def parse_published_date(self, root):
        pub_year = None
        publication_node = root.xpath(
            '(//*[@id="content"]'
            '//div[contains(concat(" ", normalize-space(@class), " "), '
            '" edition ")])[1]/div[1]//abbr/text()')
        if not publication_node:
            publication_node = root.xpath(
                '//*[@id="content"]//*[@class="items"]/div/div[1]/text()')
        for publication_value in publication_node:
            m = re.search(r'(\d{4})', publication_value)
            if m:
                pub_year = [m.group(1)]
                break
        if not pub_year:
            pub_year = root.xpath(
                '//*[@id="content"]//*[@class="items"]/div/div[1]/abbr/text()')
        try:
            pub_year = int(pub_year[0])
        except:
            return None
        # Moly normally exposes only a publication year.  Do not invent the
        # current month and day for a year-only value.
        pub_date = datetime(pub_year, 1, 1, tzinfo=utc_tz)
        return pub_date

    def parse_rating(self, root):
        rating_node = root.xpath(
            '//*[@id="content"]'
            '//*[contains(concat(" ", normalize-space(@class), " "), '
            '" rating ")]'
            '//*[contains(concat(" ", normalize-space(@class), " "), '
            '" like_count ")]/text()')
        if rating_node:
            # Calibre stores ratings on a 0-10 scale (displayed as 0-5 stars).
            return float(rating_node[0].strip('%').strip()) * 0.1

    def parse_covers(self, root):
        from calibre_plugins.moly_hu import Moly_hu
        book_covers = root.xpath(
            '(//*[contains(concat(" ", normalize-space(@class), " "), '
            '" coverbox ")]'
            '//a[contains(concat(" ", normalize-space(@class), " "), '
            '" zoom ")]/@href)[position()<=%d]' % self.max_covers)
        if book_covers:
            return [cover_url if cover_url.startswith(('http://', 'https://'))
                    else Moly_hu.BASE_URL + cover_url
                    for cover_url in book_covers]

    def parse_languages(self, tags):
        langs = []
        for tag in tags or []:
            langId = self._translateLanguageToCode(tag)
            if langId is not None:
                langs.append(langId)

        if not langs:
            return ['hu']

        return langs

    def _translateLanguageToCode(self, displayLang):
        displayLang = displayLang.lower().strip() if displayLang else None
        langTbl = {None: 'und',
                   u'angol nyelv\u0171': 'en',
                   u'n\xe9met nyelv\u0171': 'de',
                   u'francia nyelv\u0171': 'fr',
                   u'olasz nyelv\u0171': 'it',
                   u'spanyol nyelv\u0171': 'es',
                   u'orosz nyelv\u0171': 'ru',
                   u't\xf6r\xf6k nyelv\u0171': 'tr',
                   u'g\xf6r\xf6g nyelv\u0171': 'el',
                   u'k\xednai nyelv\u0171': 'zh',
                   u'jap\xe1n nyelv\u0171': 'ja'}
        return langTbl.get(displayLang, None)

    def _clean_text(self, value):
        if value is None:
            return None
        value = value.replace('\u200b', '').replace('\ufeff', '')
        return ' '.join(value.split())
