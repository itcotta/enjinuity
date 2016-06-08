# enjinuity
# Written in 2016 by David H. Wei <https://github.com/spikeh/>
#
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without any
# warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication
# along with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.
import enjinuity.objects
from selenium import webdriver
from urllib.parse import urlparse


class Scraper:

    def __init__(self, url, cookies, users):
        self.browser = webdriver.Firefox()
        self.browser.get('http://www.enjin.com/')
        for c in cookies:
            if c['domain'] == '.enjin.com':
                self.browser.add_cookie(c)
        self.url = url
        self.browser.get(url)
        hostname = urlparse(url).hostname
        for c in cookies:
            if c['domain'] == hostname:
                self.browser.add_cookie(c)
        self.browser.refresh()
        self.users = users

        self.fid = 1
        self.tid = 1
        self.pid = 1

        self.root = []

    def __del__(self):
        self.browser.quit()

    def run(self):
        categories = self.browser.find_elements_by_xpath(
            ('//div[contains(@class, "contentbox") and '
                   'contains(@class, "category")]'))
        for c in categories:
            category = enjinuity.objects.Category(c)
            self.root.append(category)

        # XXX Just one category for testing
        self.root[0].get_children(self.browser, self.users)
