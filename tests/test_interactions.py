# import json

# from contextlib import contextmanager

# from flask import url_for

# from pyquery import PyQuery as pq

# import pytest

# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys

# from conftest import (
#     get_json_config,
#     auth_valid,
#     read,
# )

# from flask_jsondash import charts_builder
# from flask_jsondash import settings


# @contextmanager
# def _webhandler():
#     browser = webdriver.Chrome()
#     try:
#         yield browser
#     finally:
#         browser.quit()


# @pytest.mark.webdriver
# def test_app_go(ctx, client):
#     app, test = client
#     with _webhandler() as browser:
#         browser.get('http://127.0.0.1:8080/charts/')
#         assert 'My app | Dashboards' in browser.title
#         elem = browser.find_element_by_name('p')
#         elem.send_keys('seleniumhq' + Keys.RETURN)
