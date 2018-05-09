import requests_mock

from flask_jsondash.data_utils import wordcloud


def test_get_word_freq_distribution():
    words = ['foo', 'foo', 'bar', 'baz']
    res = wordcloud.get_word_freq_distribution(words)
    assert dict(res) == {'foo': 2, 'bar': 1, 'baz': 1}


def test_get_word_freq_distribution_no_stopwords():
    words = ['foo', 'bar', 'baz', 'the']
    res = wordcloud.get_word_freq_distribution(words)
    assert dict(res) == {'foo': 1, 'bar': 1, 'baz': 1}


def test_get_word_freq_distribution_none():
    words = []
    res = wordcloud.get_word_freq_distribution(words)
    assert dict(res) == {}


def test_format_4_wordcloud():
    words = [('foo', 1), ('bar', 1)]
    res = wordcloud.format_4_wordcloud(words)
    assert res == [
        {'size': 2, 'text': 'foo'}, {'size': 2, 'text': 'bar'}
    ]


def test_format_4_wordcloud_sizing():
    words = [('foo', 2), ('bar', 2)]
    res = wordcloud.format_4_wordcloud(words, size_multiplier=3)
    assert res == [
        {'size': 6, 'text': 'foo'}, {'size': 6, 'text': 'bar'}
    ]


def test_format_4_wordcloud_none():
    words = []
    res = wordcloud.format_4_wordcloud(words)
    assert res == []


def test_url2wordcloud_exclude_punct(monkeypatch):
    url = 'http://www.test.com'
    content = '<html><body>; great words $ &!</body></html>'
    with requests_mock.Mocker() as m:
        m.get(url, content=content.encode('utf-8'))
        res = wordcloud.url2wordcloud(url, exclude_punct=True)
        assert isinstance(res, list)
        words = [w['text'] for w in res]
        for punct in [';', '$', '&!']:
            assert punct not in words
        for w in ['great', 'words']:
            assert w in words


def test_url2wordcloud_limit(monkeypatch):
    url = 'http://www.test.com'
    content = '<html><body>these are are great great great words</body></html>'
    with requests_mock.Mocker() as m:
        m.get(url, content=content.encode('utf-8'))
        res = wordcloud.url2wordcloud(url, limit=2)
        assert isinstance(res, list)
        words = [w['text'] for w in res]
        assert any([
            words == ['words', 'great'],
            words == ['great', 'words']
        ])


def test_url2wordcloud_min_len_none(monkeypatch):
    url = 'http://www.test.com'
    content = '<html><body>; great words short word $</body></html>'
    with requests_mock.Mocker() as m:
        m.get(url, content=content.encode('utf-8'))
        res = wordcloud.url2wordcloud(url, min_len=10)
        assert isinstance(res, list)
        words = [w['text'] for w in res]
        assert words == []


def test_url2wordcloud_min_len_none_one(monkeypatch):
    url = 'http://www.test.com'
    content = '<html><body>a a prettylongwordfortest sort word</body></html>'
    with requests_mock.Mocker() as m:
        m.get(url, content=content.encode('utf-8'))
        res = wordcloud.url2wordcloud(url, min_len=10)
        assert isinstance(res, list)
        words = [w['text'] for w in res]
        assert words == ['prettylongwordfortest']


def test_url2wordcloud_bad_url(monkeypatch):
    url = 'http://www.test.com'
    content = '<html><body>500 SERVER ERROR.</body></html>'
    with requests_mock.Mocker() as m:
        m.get(url, content=content.encode('utf-8'), status_code=404)
        res = wordcloud.url2wordcloud(url, min_len=10)
        assert res == []
