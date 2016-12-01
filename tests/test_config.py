from flask_jsondash import settings


def test_settings_have_url_keys_specified():
    for family, config in settings.CHARTS_CONFIG.items():
        assert 'js_url' in config
        assert 'css_url' in config


def test_settings_have_urls_list_or_none():
    for family, config in settings.CHARTS_CONFIG.items():
        assert any([
            isinstance(config['js_url'], list),
            config['js_url'] is None,
        ])
        assert any([
            isinstance(config['css_url'], list),
            config['css_url'] is None,
        ])


def test_all_enabled_by_default():
    for family, config in settings.CHARTS_CONFIG.items():
        assert config['enabled']


def test_valid_helplink():
    for family, config in settings.CHARTS_CONFIG.items():
        if 'help_link' in config:
            assert config['help_link'].startswith('http')
