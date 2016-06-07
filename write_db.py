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
import json
import psycopg2

with open('config.json', 'r') as f:
    config = json.load(f)

hostname = config['database']['hostname']
username = config['database']['username']
password = config['database']['password']
dbname = config['database']['dbname']
tbl_prefix = config['database']['tbl_prefix']

conn = psycopg2.connect(host=hostname, user=username, password=password,
                        database=dbname)
cur = conn.cursor()

users = pickle.load(open('users.pkl', 'rb'))
for user in users:
    query = """INSERT INTO users VALUES (
               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
               %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
               %s, %s, %s, %s);"""
    cur.execute(query, user)
conn.commit()

cur.close()
conn.close()
