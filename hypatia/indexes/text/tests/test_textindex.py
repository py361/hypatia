##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Text Index Tests
"""
import unittest

_marker = object()

class TextIndexTests(unittest.TestCase):

    def _getTargetClass(self):
        from hypatia.indexes.text import TextIndex
        return TextIndex

    def _makeOne(self, discriminator=_marker, lexicon=_marker, index=_marker):
        def _discriminator(obj, default):
            if obj is _marker:
                return default
            return obj
        if discriminator is _marker:
            discriminator = _discriminator
        if lexicon is _marker:
            if index is _marker: # defaults
                return self._getTargetClass()(discriminator=discriminator)
            else:
                return self._getTargetClass()(discriminator=discriminator,
                                              index=index)
        else:
            if index is _marker:
                return self._getTargetClass()(discriminator=discriminator,
                                              lexicon=lexicon)
            else:
                return self._getTargetClass()(discriminator=discriminator,
                                              lexicon=lexicon,
                                              index=index)

    def _makeLexicon(self, *pipeline):
        from hypatia.indexes.text.lexicon import Lexicon
        from hypatia.indexes.text.lexicon import Splitter
        if not pipeline:
            pipeline = (Splitter(),)
        return Lexicon(*pipeline)

    def _makeOkapi(self, lexicon=None, family=None):
        import BTrees
        from hypatia.indexes.text.okapiindex import OkapiIndex
        if lexicon is None:
            lexicon = self._makeLexicon()
        if family is None:
            family = BTrees.family64
        return OkapiIndex(lexicon, family=family)

    def test_class_conforms_to_IInjection(self):
        from zope.interface.verify import verifyClass
        from hypatia.interfaces import IInjection
        verifyClass(IInjection, self._getTargetClass())

    def test_instance_conforms_to_IInjection(self):
        from zope.interface.verify import verifyObject
        from hypatia.interfaces import IInjection
        verifyObject(IInjection, self._makeOne())

    def test_class_conforms_to_IIndexSearch(self):
        from zope.interface.verify import verifyClass
        from hypatia.interfaces import IIndexSearch
        verifyClass(IIndexSearch, self._getTargetClass())

    def test_instance_conforms_to_IIndexSearch(self):
        from zope.interface.verify import verifyObject
        from hypatia.interfaces import IIndexSearch
        verifyObject(IIndexSearch, self._makeOne())

    def test_class_conforms_to_IStatistics(self):
        from zope.interface.verify import verifyClass
        from hypatia.interfaces import IStatistics
        verifyClass(IStatistics, self._getTargetClass())

    def test_instance_conforms_to_IStatistics(self):
        from zope.interface.verify import verifyObject
        from hypatia.interfaces import IStatistics
        verifyObject(IStatistics, self._makeOne())

    def test_class_conforms_to_ICatalogIndex(self):
        from zope.interface.verify import verifyClass
        from hypatia.interfaces import ICatalogIndex
        verifyClass(ICatalogIndex, self._getTargetClass())

    def test_instance_conforms_to_ICatalogIndex(self):
        from zope.interface.verify import verifyObject
        from hypatia.interfaces import ICatalogIndex
        verifyObject(ICatalogIndex, self._makeOne())

    def test_class_conforms_to_IIndexSort(self):
        from zope.interface.verify import verifyClass
        from hypatia.interfaces import IIndexSort
        verifyClass(IIndexSort, self._getTargetClass())

    def test_instance_conforms_to_IIndexSort(self):
        from zope.interface.verify import verifyObject
        from hypatia.interfaces import IIndexSort
        verifyObject(IIndexSort, self._makeOne())

    def test_ctor_defaults(self):
        index = self._makeOne()
        from hypatia.indexes.text.lexicon import CaseNormalizer
        from hypatia.indexes.text.lexicon import Lexicon
        from hypatia.indexes.text.lexicon import Splitter
        from hypatia.indexes.text.lexicon import StopWordRemover
        from hypatia.indexes.text.okapiindex import OkapiIndex
        self.failUnless(isinstance(index.index, OkapiIndex))
        self.failUnless(isinstance(index.lexicon, Lexicon))
        self.failUnless(index.index._lexicon is index.lexicon)
        pipeline = index.lexicon._pipeline
        self.assertEqual(len(pipeline), 3)
        self.failUnless(isinstance(pipeline[0], Splitter))
        self.failUnless(isinstance(pipeline[1], CaseNormalizer))
        self.failUnless(isinstance(pipeline[2], StopWordRemover))

    def test_ctor_explicit_lexicon(self):
        from hypatia.indexes.text.okapiindex import OkapiIndex
        lexicon = object()
        index = self._makeOne(lexicon=lexicon)
        self.failUnless(index.lexicon is lexicon)
        self.failUnless(isinstance(index.index, OkapiIndex))
        self.failUnless(index.index._lexicon is lexicon)

    def test_ctor_explicit_index(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(index=okapi)
        self.failUnless(index.index is okapi)
        # See LP #232516
        self.failUnless(index.lexicon is lexicon)

    def test_ctor_explicit_lexicon_and_index(self):
        lexicon = object()
        okapi = DummyIndex()
        index = self._makeOne(lexicon=lexicon, index=okapi)
        self.failUnless(index.lexicon is lexicon)
        self.failUnless(index.index is okapi)

    def test_ctor_callback_discriminator(self):
        def _discriminator(obj, default):
            """ """
        index = self._makeOne(discriminator=_discriminator)
        self.failUnless(index.discriminator is _discriminator)

    def test_ctor_string_discriminator(self):
        index = self._makeOne(discriminator='abc')
        self.assertEqual(index.discriminator, 'abc')

    def test_ctor_bad_discriminator(self):
        self.assertRaises(ValueError, self._makeOne, object())

    def test_index_doc(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon=lexicon, index=okapi)
        index.index_doc(1, 'cats and dogs')
        self.assertEqual(okapi._indexed[0], (1, 'cats and dogs'))

    def test_index_doc_then_missing_value(self):
        index = self._makeOne()
        index.index_doc(3, u'Am I rich yet?')
        self.assertEqual(set([3]), set(index.applyContains('rich')))
        self.failUnless(3 in index.docids())
        index.index_doc(3, _marker)
        self.assertEqual(set(), set(index.applyEq('rich')))
        self.failUnless(3 in index.docids())

    def test_index_doc_missing_value_then_with_value(self):
        index = self._makeOne()
        index.index_doc(20, _marker)
        self.assertEqual(set(), set(index.applyContains('rich')))
        self.failUnless(20 in index.docids())
        index.index_doc(20, u'Am I rich yet?')
        self.assertEqual(set([20]), set(index.applyContains('rich')))
        self.failUnless(20 in index.docids())

    def test_index_doc_missing_value_then_unindex(self):
        index = self._makeOne()
        index.index_doc(20, _marker)
        self.assertEqual(set(), set(index.applyEq('/cmr')))
        self.failUnless(20 in index.docids())
        index.unindex_doc(20)
        self.assertEqual(set(), set(index.applyEq('/cmr')))
        self.failIf(20 in index.docids())

    def test_unindex_doc(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon=lexicon, index=okapi)
        index.unindex_doc(1)
        self.assertEqual(okapi._unindexed[0], 1)

    def test_unindex_doc_removes_from_docids(self):
        index = self._makeOne()
        index.index_doc(20, _marker)
        self.failUnless(20 in index.docids())
        index.unindex_doc(20)
        self.failIf(20 in index.docids())

    def test_reindex_doc_doesnt_unindex(self):
        index = self._makeOne()
        index.index_doc(5, 'now is the time')
        index.unindex_doc = lambda *args, **kw: 1/0
        index.reindex_doc(5, 'now is the time')

    def test_clear(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon=lexicon, index=okapi)
        index.clear()
        self.failUnless(okapi._cleared)

    def test_documentCount(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon=lexicon, index=okapi)
        self.assertEqual(index.documentCount(), 4)

    def test_wordCount(self):
        lexicon = object()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon=lexicon, index=okapi)
        self.assertEqual(index.wordCount(), 45)

    def test_apply_no_results(self):
        lexicon = DummyLexicon()
        okapi = DummyOkapi(lexicon, {})
        index = self._makeOne(lexicon=lexicon, index=okapi)
        self.assertEqual(index.apply('anything'), {})
        self.assertEqual(okapi._query_weighted, [])
        self.assertEqual(okapi._searched, ['anything'])

    def test_apply_w_results(self):
        lexicon = DummyLexicon()
        okapi = DummyOkapi(lexicon)
        index = self._makeOne(lexicon=lexicon, index=okapi)
        results = index.apply('anything')
        self.assertEqual(results[1], 14.0 / 42.0)
        self.assertEqual(results[2], 7.4 / 42.0)
        self.assertEqual(results[3], 3.2 / 42.0)
        self.assertEqual(okapi._query_weighted[0], ['anything'])
        self.assertEqual(okapi._searched, ['anything'])

    def test_apply_w_results_zero_query_weight(self):
        lexicon = DummyLexicon()
        okapi = DummyOkapi(lexicon)
        okapi._query_weight = 0
        index = self._makeOne(lexicon=lexicon, index=okapi)
        results = index.apply('anything')
        self.assertEqual(results[1], 14.0)
        self.assertEqual(results[2], 7.4)
        self.assertEqual(results[3], 3.2)
        self.assertEqual(okapi._query_weighted[0], ['anything'])
        self.assertEqual(okapi._searched, ['anything'])

    def test_apply_w_results_bogus_query_weight(self):
        import sys
        DIVISOR = sys.maxint / 10
        lexicon = DummyLexicon()
        # cause TypeError in division
        okapi = DummyOkapi(lexicon, {1: '14.0', 2: '7.4', 3: '3.2'})
        index = self._makeOne(lexicon=lexicon, index=okapi)
        results = index.apply('anything')
        self.assertEqual(results[1], DIVISOR)
        self.assertEqual(results[2], DIVISOR)
        self.assertEqual(results[3], DIVISOR)
        self.assertEqual(okapi._query_weighted[0], ['anything'])
        self.assertEqual(okapi._searched, ['anything'])

    def test_applyDoesNotContain(self):
        index = self._makeOne()
        index.index_doc(1, u'now is the time')
        index.index_doc(2, u"l'ora \xe9 ora")
        result = sorted(index.applyDoesNotContain('time'))
        self.assertEqual(result, [2])

    def test_applyDoesNotContain_with_unindexed_doc(self):
        def discriminator(obj, default):
            if isinstance(obj, basestring):
                return obj
            return default
        index = self._makeOne(discriminator)
        index.index_doc(1, u'now is the time')
        index.index_doc(2, u"l'ora \xe9 ora")
        index.index_doc(3, 3)
        result = sorted(index.applyDoesNotContain('time'))
        self.assertEqual(result, [2, 3])

    def test_applyDoesNotContain_nothing_indexed(self):
        def discriminator(obj, default):
            return default
        index = self._makeOne(discriminator)
        index.index_doc(1, u'now is the time')
        index.index_doc(2, u"l'ora \xe9 ora")
        index.index_doc(3, 3)
        result = sorted(index.applyDoesNotContain('time'))
        self.assertEqual(result, [1, 2, 3])
        
    def test_sort_no_results(self):
        index = self._makeOne()
        self.assertEqual([], index.sort([]))

    def test_sort_without_weights(self):
        index = self._makeOne()
        self.assertRaises(TypeError, index.sort, [1])

    def test_sort_unlimited_forward(self):
        index = self._makeOne()
        results = {-2: 5.0, 3: 3.0, 0: 4.5}
        expect = [-2, 0, 3]
        self.assertEqual(index.sort(results), expect)

    def test_sort_unlimited_reverse(self):
        index = self._makeOne()
        results = {-2: 5.0, 3: 3.0, 0: 4.5}
        expect = [3, 0, -2]
        self.assertEqual(index.sort(results, reverse=True), expect)

    def test_sort_limited(self):
        index = self._makeOne()
        results = {-2: 5.0, 3: 3.0, 0: 4.5}
        expect = [-2, 0]
        self.assertEqual(index.sort(results, limit=2), expect)

    def test_docids(self):
        index = self._makeOne()
        index.index_doc(1, u'now is the time')
        index.index_doc(2, u"l'ora \xe9 ora")
        index.index_doc(3, u"you have nice hair.")
        self.assertEqual(set(index.docids()), set((1, 2, 3)))

    def test_docids_with_indexed_and_not_indexed(self):
        index = self._makeOne()
        index.index_doc(1, u'Am I rich yet?')
        index.index_doc(2, _marker)
        self.assertEqual(set([1, 2]), set(index.docids()))
        
class DummyOkapi:

    _cleared = False
    _document_count = 4
    _word_count = 45
    _query_weight = 42.0

    def __init__(self, lexicon, search_results=None):
        self.lexicon = lexicon
        self._indexed = []
        self._unindexed = []
        self._searched = []
        self._query_weighted = []
        if search_results is None:
            search_results = {1: 14.0, 2: 7.4, 3: 3.2}
        self._search_results = search_results

    def index_doc(self, docid, text):
        self._indexed.append((docid, text))

    def unindex_doc(self, docid):
        self._unindexed.append(docid)

    def clear(self):
        self._cleared = True

    def documentCount(self):
        return self._document_count

    def wordCount(self):
        return self._word_count

    def query_weight(self, terms):
        self._query_weighted.append(terms)
        return self._query_weight

    def search(self, term):
        self._searched.append(term)
        return self._search_results

    search_phrase = search_glob = search

class DummyLexicon:
    def parseTerms(self, term):
        return term

class DummyIndex:
    def clear(self):
        self.cleared = True

def test_suite():
    return unittest.TestSuite((
                      unittest.makeSuite(TextIndexTests),
                    ))
