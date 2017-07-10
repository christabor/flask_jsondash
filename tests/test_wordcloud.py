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
