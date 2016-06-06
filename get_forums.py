#!/usr/bin/env python
# enjin-scraper
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
import pickle
import selenium
from selenium import webdriver

cookies = pickle.load(open('essence.pkl', 'rb'))
browser = webdriver.Firefox()

browser.get('http://www.enjin.com/')
for c in cookies:
    if c['domain'] == '.enjin.com':
        browser.add_cookie(c)

browser.get('http://essencesunstrider.enjin.com/home')
for c in cookies:
    if c['domain'] == 'essencesunstrider.enjin.com':
        browser.add_cookie(c)

browser.get('http://essencesunstrider.enjin.com/forum')
cat_xp = ("//div[contains(@class, 'contentbox') and "
                "contains(@class, 'category')]")
categories = browser.find_elements_by_xpath(cat_xp)
for category in categories:
    cn_xp = 'div[@class="block-title"]/div[@class="text"]/span'
    cname = category.find_element_by_xpath(cn_xp)
    print(cname.text)
    f_xp = 'div[@class="block-container "]//td[@class="c forum"]'
    forums = category.find_elements_by_xpath(f_xp)
    for forum in forums:
        fname = forum.find_element_by_xpath('div[1]/a')
        fdesc = forum.find_element_by_xpath('div[2]')
        print('\t', fname.text)
        print('\t', fdesc.text)
browser.quit()
