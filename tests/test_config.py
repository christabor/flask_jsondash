from flask_jsondash import settings


def test_settings_have_url_keys_specified():
    for family, config in settings.CHARTS_CONFIG.items():
        assert 'js_url' in config
        assert 'css_url' in config


def test_settings_have_urls_list_or_none():
    for family, config in settings.CHARTS_CONFIG.items():
        assert isinstance(config['js_url'], list)
        assert isinstance(config['css_url'], list)


def test_all_enabled_by_default():
    for family, config in settings.CHARTS_CONFIG.items():
        assert config['enabled']


def test_valid_helplink():
    for family, config in settings.CHARTS_CONFIG.items():
        if 'help_link' in config:
            assert config['help_link'].startswith('http')


def test_families_with_dependencies_are_valid_in_config():
    families = list(settings.CHARTS_CONFIG.keys())
    for family, config in settings.CHARTS_CONFIG.items():
        if config['dependencies']:
            for dep in config['dependencies']:
                assert dep in families
