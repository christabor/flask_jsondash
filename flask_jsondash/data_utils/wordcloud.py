#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
flask_jsondash.data_utils.wordcloud
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Utilities for working with wordcloud formatted data.

:copyright: (c) 2016 by Chris Tabor.
:license: MIT, see LICENSE for more details.
"""

from collections import Counter
from string import punctuation
import re

import requests
from pyquery import PyQuery as Pq

# Py2/3 compat.
try:
    _unicode = unicode
except NameError:
    _unicode = str


# NLTK stopwords
stopwords = [
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
    'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she',
    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their',
    'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
    'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
    'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now',
]


def get_word_freq_distribution(words):
    """Get the counted word frequency distribution of all words.

    Arg:
        words (list): A list of strings indicating words.

    Returns:
        collections.Counter: The Counter object with word frequencies.
    """
    return Counter([w for w in words if w not in stopwords])


def format_4_wordcloud(words, size_multiplier=2):
    """Format words in a way suitable for wordcloud plugin.

    Args:
        words (list): A list 2-tuples of format: (word-string, occurences).
        size_multiplier (int, optional): The size multiplier to scale
            word sizing. Can improve visual display of word cloud.

    Returns:
        list: A list of dicts w/ appropriate keys.
    """
    return [
        {'text': word, 'size': size * size_multiplier}
        for (word, size) in words if word
    ]


def url2wordcloud(url, requests_kwargs={},
                  exclude_punct=True,
                  normalized=True,
                  limit=None,
                  size=1,
                  min_len=None):
    """Convert the text content of a urls' html to a wordcloud config.

    Args:
        url (str): The url to load.
        requests_kwargs (dict, optional): The kwargs to pass to the
            requests library. (e.g. auth, headers, mimetypes)
        exclude_punc (bool, optional): exclude punctuation
        min_length (int, optional): the minimum required length, if any
        limit (int, optional): the number of items to limit
            (by most common), if any
        normalized (bool, optional): normalize data by
            lowercasing and strippping whitespace

    Returns:
        same value as :func:`~format_4_wordcloud`
    """
    resp = requests.get(url, **requests_kwargs)
    if not resp.status_code == 200:
        return []
    resp = Pq(resp.content).find('body').text().split(' ')
    if exclude_punct:
        resp = [
            re.sub(r'[^a-zA-Z0-9]+', '', w) for w
            in resp if w not in punctuation
        ]
    if min_len is not None:
        resp = [w for w in resp if len(w) >= min_len]
    if normalized:
        resp = [w.lower() for w in resp]
    words = get_word_freq_distribution(resp)
    if limit is not None:
        words = words.most_common(limit)
    else:
        words = [(k, v) for k, v in words.items()]
    return format_4_wordcloud(words, size_multiplier=size)
