import requests
import html2text
import json
import os
import time

from bs4 import BeautifulSoup
from config import setup_logging
from urllib.parse import urljoin, urlparse
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException

#set firefox location
#FIREFOX_LOCATION = os.environ.get('FIREFOX_LOCATION', os.getenv('FIREFOX_LOCATION'))

# Configure logging
logging = setup_logging()

# Set Browserless API key
browserless_api_key = os.environ.get('BROWSERLESS_API_KEY', os.getenv('BROWSERLESS_API_KEY'))

# Set header information
user_agent = 'Mozilla/5.0 (Linux; Android 11; 100011886A Build/RP1A.200720.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.69 Safari/537.36'
sec_ch_ua = '"Google Chrome";v="104", " Not;A Brand";v="105", "Chromium";v="104"'
referer = 'https://www.google.com'
cache_control = 'no-cache'
content_type = 'application/json'

# This function intercepts a request and modifies its headers
def interceptor(request):
