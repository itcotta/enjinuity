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
import datetime
import pickle
import selenium
from selenium import webdriver
from urllib.parse import urlparse

DEFAULT_FORUM = [
    1,  # disporder
    1,  # active
    1,  # open
    0,  # threads
    0,  # posts
    0,  # lastpost
    0,  # lastposter
    0,  # lastposteruid
    0,  # lastposttid
    '', # lastpostsubject
    0,  # allowhtml
    1,  # allowmycode
    1,  # allowsmilies
    1,  # allowimgcode
    1,  # allowvideocode
    1,  # allowpicons
    1,  # allowtratings
    1,  # usepostcounts
    1,  # usethreadcounts
    0,  # requireprefix
    '', # password
    1,  # showinjump
    0,  # style
    0,  # overridestyle
    0,  # rulestype
    '', # rulestitle
    '', # rules
    0,  # unapprovedthreads
    0,  # unapprovedposts
    0,  # deletedthreads
    0,  # deletedposts
    0,  # defaultdatecut
    '', # defaultsortby
    ''  # defaultsortorder
]

DEFAULT_THREAD = []

DEFAULT_POST = []

XPATH_CATEGORY = ('//div[contains(@class, "contentbox") and '
                        'contains(@class, "category")]')

XPATH_SUBFORUM = ('//div[contains(@class, "contentbox") and '
                        'contains(@class, "subforums-block")]')

XPATH_THREAD = ('//div[contains(@class, "contentbox") and '
                      'contains(@class, "threads")]')

XPATH_POST = ('//div[contains(@class, "contentbox") and '
                    'contains(@class, "posts")]')


def add_category(elem, fid, p_fid, out):
    cname = elem.find_element_by_xpath(
      'div[@class="block-title"]/div[@class="text"]/span')
    out.append([
      fid,        # fid
      cname.text, # name
      '',         # description
      '',         # linkto
      'c',        # type
      p_fid,      # pid
      str(fid)    # parentlist
    ] + DEFAULT_FORUM)


def add_forum(elem, fid, p_fid, plist, out):
    fname = elem.find_element_by_xpath('div[1]/a')
    fdesc = elem.find_element_by_xpath('div[2]')
    out.append([
      fid,        # fid
      fname.text, # name
      fdesc.text, # description
      '',         # linkto
      'f',        # type
      p_fid,      # pid
      plist,      # parentlist
    ] + DEFAULT_FORUM)
    return fname.get_attribute('href')


def add_post(elem, pid, tid, fid, rt, subject, out):
    username = elem.find_element_by_xpath('td[1]/div[1]/div[1]/a')
    post = elem.find_element_by_xpath('td[2]/div[1]/div[1]')
    # Posted Jan 23, 15 · OP · Last edited Apr 29, 16
    posttime = elem.find_element_by_xpath('td[2]/div[2]/div[1]/div[1]')
    posttime = posttime.text.split(' · ')
    edittime = 0
    if len(posttime) == 3:
        edittime = datetime.datetime.strptime(posttime[2],
                                              "Last edited %b %d, %y")
        edittime = edittime.replace(tzinfo=datetime.timezone.utc).timestamp()
    # posttime[0] always exists
    dateline = datetime.datetime.strptime(posttime[0], "Posted %b %d, %y")
    dateline = dateline.replace(tzinfo=datetime.timezone.utc).timestamp()
    uid = 0
    if username.text in users:
        uid = users[username.text]
    # Assumes that edits are done by the original poster
    edituid = 0
    if edittime > 0:
        edituid = uid
    out.append([
        pid,
        tid,
        rt,     # replyto, 0 for OP, 1 otherwise
        fid,
        subject,
        0,      # icon
        uid,
        username.text,
        int(dateline),
        'this is a default message.',
        '',     # ipaddress
        0,      # includesig
        0,      # smilieoff
        edituid,
        int(edittime),
        '',     # editreason
        1       # visible
    ])


def add_thread(url, pid, tid, fid, subject, out_posts):
    browser.get(url)
    post_block = browser.find_element_by_xpath(XPATH_POST)
    posts = post_block.find_elements_by_xpath(
      'div[@class="block-container"]//tr[contains(@class, "row")]')
    re_subject = 'RE: ' + subject
    for i, p in enumerate(posts):
        if i == 0:
            add_post(p, pid, tid, fid, 0, subject, out_posts)
        else:
            add_post(p, pid, tid, fid, 1, re_subject, out_posts)
        pid += 1


def walk_forum(url, fid, p_fid, plist, tid, pid, out_forums, out_threads,
               out_posts):
    browser.get(url)
    t_children = []
    f_children = []
    curr_fid = fid

    # Threads
    thread_block = browser.find_element_by_xpath(XPATH_THREAD)
    threads = thread_block.find_elements_by_xpath(
      'div[@class="block-container"]//tr[contains(@class, "row")]')
    for t in threads:
        # Used to identify sticky, locked threads
        tprops = t.find_element_by_xpath('td[1]/a/div').get_attribute(
          'class').split(' ')
        tname = t.find_element_by_xpath(
          ('td[2]/a[contains(@class, "thread-view") and '
                   'contains(@class, "thread-subject")]'))
        tlink = tname.get_attribute('href')
        t_children.append((tlink, tid, tname.text))
        tid += 1

    # Subforums
    try:
        subforum_block = browser.find_element_by_xpath(XPATH_SUBFORUM)
        subforums = subforum_block.find_elements_by_xpath(
          'div[@class="block-container"]//td[@class="c forum"]')
        for f in subforums:
            _plist = plist + ',' + str(fid)
            flink = add_forum(f, fid, p_fid, _plist, out_forums)
            # Forums can be external links
            tld = urlparse(flink).hostname.split('.')[-2]
            if tld == 'enjin':
                f_children.append((flink, fid, _plist))
            fid += 1

        # Recursively walk subforums
        for child_url, parent_fid, parentlist in f_children:
            fid = walk_forum(child_url, fid, parent_fid, parentlist, tid, pid,
                             out_forums, out_threads, out_posts)
    except selenium.common.exceptions.NoSuchElementException:
        # No subforums
        pass

    for thread_url, p_tid, subject in t_children:
        thread_data = add_thread(thread_url, pid, p_tid, curr_fid, subject,
                                 out_posts)

    return fid


if __name__ == "__main__":
    cookies = pickle.load(open('essence.pkl', 'rb'))
    users = pickle.load(open('users_map.pkl', 'rb'))
    browser = webdriver.Firefox()

    browser.get('http://www.enjin.com/')
    for c in cookies:
        if c['domain'] == '.enjin.com':
            browser.add_cookie(c)

    browser.get('http://essencesunstrider.enjin.com/home')
    for c in cookies:
        if c['domain'] == 'essencesunstrider.enjin.com':
            browser.add_cookie(c)

    fid = 4
    p_fid = 0
    tid = 1
    pid = 1
    children = []

    out_forums = []
    out_threads = []
    out_posts = []

    browser.get('http://essencesunstrider.enjin.com/forum')
    # Forum root
    categories = browser.find_elements_by_xpath(XPATH_CATEGORY)
    for c in categories:
        add_category(c, fid, p_fid, out_forums)
        # Forums are considered their category's children
        category_fid = fid
        fid += 1

        forums = c.find_elements_by_xpath(
          'div[@class="block-container "]//td[@class="c forum"]')
        for f in forums:
            _plist = str(category_fid) + ',' + str(fid)
            flink = add_forum(f, fid, category_fid, _plist, out_forums)
            # Forums can be external links
            tld = urlparse(flink).hostname.split('.')[-2]
            if tld == 'enjin':
                children.append((flink, fid, _plist))
            fid += 1

    # Recursively add each forum
    for child_url, parent_fid, parentlist in children:
        walk_forum(child_url, fid, parent_fid, parentlist, tid, pid, out_forums,
                   out_threads, out_posts)

    browser.quit()

    #pickle.dump(out, open('forums.pkl', 'wb'))
