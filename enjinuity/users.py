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
import hashlib
import pickle
import random
import string
import time

def random_string(length):
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase +
        string.ascii_uppercase + string.digits) for _ in range(length))

def md5(string):
    return hashlib.md5(string.encode()).hexdigest()


class Users:

    def __init__(self, users, email, passwd, uid):
        with open(users, 'r') as f:
            self.users = [u.rstrip() for u in f]
        self.email = email
        self.passwd = passwd
        self.uid = uid

        # Database-specific output
        self.out = []
        # Map of username->uid
        self.user_map = {}

    def get_uid(self, user):
        try:
            return self.user_map[user]
        except KeyError:
            return 0

    def dump(self, filename):
        pickle.dump(self.out, open(filename, 'wb'))


class MyBBUsers(Users):

    def __init__(self, users, email, passwd, uid):
        super().__init__(users, email, passwd, uid)
        # http://docs.mybb.com/1.6/Database-Tables-mybb-users/
        for user in self.users:
            salt = random_string(8)
            saltedpw = md5(md5(salt) + self.passwd)
            loginkey = random_string(50)
            now = int(time.time())
            self.out.append([
                self.uid,
                user,
                saltedpw,
                salt,
                loginkey,
                self.email,
                0,          # postnum
                0,          # threadnum
                '',         # avatar
                '',         # avatardimensions
                0,          # avatartype
                2,          # usergroup
                '',         # additionalgroups
                0,          # displaygroup
                '',         # usertitle
                now,        # regdate
                now,        # lastactive
                now,        # lastvisit
                0,          # lastpost
                '',         # website
                '',         # icq
                '',         # aim
                '',         # yahoo
                '',         # skype
                '',         # google
                '',         # birthday
                'all',      # birthdayprivacy
                '',         # signature
                1,          # allownotices
                0,          # hideemail
                0,          # subscriptionmethod
                0,          # invisible
                1,          # receivepms
                0,          # receivefrombuddy
                1,          # pmnotice
                1,          # pmnotify
                1,          # buddyrequestspm
                0,          # buddyrequestsauto
                'linear',   # threadmode
                1,          # showimages
                1,          # showvideos
                1,          # showsigs
                1,          # showavatars
                1,          # showquickreply
                1,          # showredirect
                0,          # ppp
                0,          # tpp
                0,          # daysprune
                '',         # dateformat
                '',         # timeformat
                0,          # timezone
                0,          # dst
                0,          # dstcorrection
                '',         # buddylist
                '',         # ignorelist
                0,          # style
                0,          # away
                0,          # awaydate
                0,          # returndate
                '',         # awayreason
                '',         # pmfolders
                '',         # notepad
                0,          # referrer
                0,          # referrals
                0,          # reputation
                '',         # regip
                '',         # lastip
                '',         # language
                0,          # timeonline
                1,          # showcodebuttons
                0,          # totalpms
                0,          # unreadpms
                0,          # warningpoints
                0,          # moderateposts
                0,          # moderationtime
                0,          # suspendposting
                0,          # suspensiontime
                0,          # suspendsignature
                0,          # suspendsigtime
                0,          # coppauser
                0,          # classicpostbit
                1,          # loginattempts
                '',         # usernotes
                0           # sourceeditor
            ])
            self.user_map[user] = uid
            uid += 1
