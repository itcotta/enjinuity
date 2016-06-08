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
from datetime import datetime, timezone
from selenium.common.exceptions import NoSuchElementException


class FObject:

    def __init__(self, parent):
        self.parent = parent
        self.children = []
        self.children_to_get = []


class Post(FObject):

    def __init__(self, elem, thread, subject, users):
        super().__init__(thread)
        self.subject = subject
        self.author = elem.find_element_by_xpath('td[1]/div[1]/div[1]/a').text
        self.uid = users.get_uid(self.author)

        # TODO Other strings i.e. "x minutes ago", "y hours ago"...
        # Posted Jan 23, 15 · OP · Last edited Apr 29, 16
        time_elem = elem.find_element_by_xpath('td[2]/div[2]/div[1]/div[1]')
        time_list = time_elem.text.split(' · ')

        self.posttime = datetime.strptime(
          time_list[0], "Posted %b %d, %y").replace(
          tzinfo=timezone.utc).timestamp()

        self.edituid = 0
        self.edittime = 0
        if len(time_list) == 3:
            self.edituid = self.uid if time_list[1] == 'OP' else users.get_uid(
              time_list[1])
            self.edittime = datetime.strptime(
              time_list[2], "Last edited %b %d, %y").replace(
              tzinfo=timezone.utc).timestamp()

        msg_elem = elem.find_element_by_xpath('td[2]/div[1]/div[1]')
        self.message = 'Default message.'

    def get_uid(self):
        return self.uid

    def get_author(self):
        return self.author

    def get_posttime(self):
        return self.posttime

    def format_mybb(self, pid, tid, fid, rt):
        out = [
            pid,        # pid
            tid,
            rt,         # replyto, 0 for OP, 1 otherwise
            fid,
            self.subject,
            0,          # icon
            self.uid,
            self.author,
            self.posttime,
            self.message,
            '',         # ipaddress
            0,          # includesig
            0,          # smilieoff
            self.edituid,
            self.edittime,
            '',         # editreason
            1           # visible
        ]
        return out

    def format_phpbb(self):
        raise NotImplementedError


# http://.../viewthread/... page
class Thread(FObject):

    def __init__(self, elem, forum, users):
        # TODO Thread views from parent
        super().__init__(forum)
        posts_elem = elem.find_element_by_xpath(
          '//div[@class="contentbox posts"]')

        # TODO Flags enum
        self.flags = posts_elem.find_element_by_xpath(
          'div[1]/div[3]/span/div[1]/div[1]').get_attribute('class').split(' ')
        self.subject = posts_elem.find_element_by_xpath(
          'div[1]/div[3]/span/h1').text

        posts = posts_elem.find_elements_by_xpath(
          'div[2]//tr[contains(@class, "row")]')

        # First post
        op = Post(posts[0], self, self.subject, users)
        self.opuid = op.get_uid()
        self.opauthor = op.get_author()
        self.optime = op.get_posttime()
        # TODO OP pid
        self.children.append(op)

        # Rest of the replies
        re_subject = 'RE: ' + self.subject
        for p in posts[1:]:
            reply = Post(p, self, re_subject, users)
            self.children.append(reply)
        self.replies = len(self.children)

        lp = self.children[-1]

        # Last post
        self.lptime = lp.get_posttime()
        self.lpauthor = lp.get_author()
        self.lpuid = lp.get_uid()

    def format_mybb(self):
        raise NotImplementedError

    def format_phpbb(self):
        raise NotImplementedError


# http://.../viewforum/... page
class Forum(FObject):

    def __init__(self, name, desc, elem, parent):
        super().__init__(parent)
        # TODO If a forum is an external link
        self.name = name
        self.desc = desc

        # Subforums
        try:
            subforums = elem.find_elements_by_xpath(
              ('//div[contains(@class, "contentbox") and '
                     'contains(@class, "subforums-block")]/div[2]'
               '//tr[contains(@class, "row")]'))
            for sf in subforums:
                sf_name = sf.find_element_by_xpath('td[2]/div[1]/a')
                sf_desc = sf.find_element_by_xpath('td[2]/div[2]')
                sf_url = sf_name.get_attribute('href')
                self.children_to_get.append((sf_name, sf_desc, sf_url))
        except NoSuchElementException:
            pass

        # Threads
        threads = elem.find_elements_by_xpath(
          ('//div[@class="contentbox threads"]/div[2]'
           '//tr[contains(@class, "row")]'))
        for t in threads:
            t_name = t.find_element_by_xpath(
              ('td[2]/a[contains(@class, "thread-view") and '
                       'contains(@class, "thread-subject")]'))
            t_url = t_name.get_attribute('href')
            self.children_to_get.append((t_url,))

    def get_children(self, browser, users):
        for child in self.children_to_get:
            # Check if the child is a subforum or thread
            if len(child) == 3:
                c_name, c_desc, c_url = child
                browser.get(c_url)
                c_body = browser.find_element_by_tag_name('body')
                forum = Forum(c_name, c_desc, c_body, self)
                self.children.append(forum)
            else:
                c_url = child[0]
                browser.get(c_url)
                c_body = browser.find_element_by_tag_name('body')
                thread = Thread(c_body, self, users)
                self.children.append(thread)

        for child in self.children:
            try:
                child.get_children(browser, users)
            except AttributeError:
                pass

    def format_mybb(self):
        raise NotImplementedError

    def format_phpbb(self):
        raise NotImplementedError


class Category(FObject):

    def __init__(self, elem):
        # A category has no parents
        super().__init__(None)
        self.name = elem.find_element_by_xpath('div[1]/div[3]/span').text

        forums = elem.find_elements_by_xpath('div[2]//td[@class="c forum"]')
        for f in forums:
            f_name = f.find_element_by_xpath('div[1]/a')
            f_desc = f.find_element_by_xpath('div[2]')
            f_url = f_name.get_attribute('href')
            self.children_to_get.append((f_name.text, f_desc.text, f_url))

    def get_children(self, browser, users):
        for c_name, c_desc, c_url in self.children_to_get:
            browser.get(c_url)
            c_body = browser.find_element_by_tag_name('body')
            forum = Forum(c_name, c_desc, c_body, self)
            self.children.append(forum)

        for forum in self.children:
            forum.get_children(browser, users)

    def format_mybb(self):
        raise NotImplementedError

    def format_phpbb(self):
        raise NotImplementedError
