# -*- coding: UTF-8 -*-
"""
Dirty command to get old structurred data from db 'ella'.
"""
from optparse import make_option
import urllib
import os, os.path
import MySQLdb as mysql
from time import sleep

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.contrib.sites.models import Site

from ella.core.models import Category, Author, Source
from ella.newman.models import CategoryUserRole, DenormalizedCategoryUserRole
from ella.articles.models import Article, ArticleContents
from ella.photos.models import Photo

conn = None # global variable holds connection to database

BEFORE_DOWNLOAD_SLEEP = 0.02

SQL_ALL_ARTICLES = """
SELECT 
    id, 
    title, 
    upper_title,
    slug,
    perex,
    created,
    updated, 
    source_id,
    category_id,
    photo_id
FROM
    articles_article
ORDER BY
    created
"""

SQL_ALL_ARTICLE_CONTENTS = """
SELECT
    id,
    article_id,
    title,
    content
FROM
    articles_articlecontents
"""

SQL_ARTICLE_AUTHORS = """
SELECT
    id,
    article_id,
    author_id
FROM
    articles_article_authors
WHERe
    article_id = %s
"""

SQL_ALL_AUTHORS = """
SELECT
    id,
    user_id,
    name,
    slug,
    description,
    text
FROM
    core_author
"""

SQL_REMAINING_CATEGORIES = """
SELECT
    id, 
    title, 
    slug,
    tree_parent_id,
    tree_path,
    description,
    site_id
FROM
    core_category
WHERE 
    tree_parent_id IS NOT NULL
"""

SQL_PARENT_CATEGORIES = """
SELECT
    id, 
    title, 
    slug,
    tree_parent_id,
    tree_path,
    description,
    site_id
FROM
    core_category
WHERE
    tree_parent_id IS NULL
"""

SQL_CHILDREN_CATEGORIES = """
SELECT
    id, 
    title, 
    slug,
    tree_parent_id,
    tree_path,
    description,
    site_id
FROM
    core_category
WHERE
    tree_parent_id = %s
"""

SQL_ALL_SITES = """
SELECT id, domain, name FROM django_site
"""

SQL_ALL_SOURCES = """
SELECT
    id,
    name,
    url,
    description
FROM
    core_source
"""

SQL_ALL_PHOTOS = """
SELECT
    id,
    title,
    description,
    slug,
    image,
    height,
    source_id,
    created
FROM
    photos_photo,
    __tmp_article_ids
WHERE
    id = __tmp_article_ids.photo_id
"""

SQL_ARTICLE_IDS = """
CREATE TEMPORARY TABLE __tmp_article_ids
SELECT
    photo_id
FROM
    articles_article
WHERE
    photo_id IS NOT NULL
GROUP BY
    photo_id
ORDER BY
    photo_id DESC
"""

site_map = {}     # key .. old ID, value .. new Site 
category_map = {} # key .. old ID, value .. new Category
char_encoding = None
source_map = {}
photo_map = {}
article_map = {}
author_map = {}

def map_sites():
    cur = conn.cursor()
    cur.execute(SQL_ALL_SITES)
    num = int(cur.rowcount)
    for idx in range(num):
        row = cur.fetchone()
        if row[2]:
            print 'Adding Site: domain=%s name=%s' % (row[1], row[2])
            obj, created = Site.objects.get_or_create(domain=row[1], name=row[2])
            site_map[int(row[0])] = obj

def map_article_contents():
    cur = conn.cursor()
    cur.execute(SQL_ALL_ARTICLE_CONTENTS)
    num = int(cur.rowcount)
    for idx in range(num):
        row = cur.fetchone()
        print 'Adding A.Contents: title=%s' % (row[2],)
        obj, created = ArticleContents.objects.get_or_create(
            title=row[2],
            content=row[3],
            article=article_map[int(row[1])]
        )


def map_sources():
    cur = conn.cursor()
    cur.execute(SQL_ALL_SOURCES)
    num = int(cur.rowcount)
    for idx in range(num):
        row = cur.fetchone()
        print 'Adding Source: name=%s url=%s' % (row[1], row[2])
        obj, created = Source.objects.get_or_create(name=row[1], url=row[2], description=row[3])
        source_map[int(row[0])] = obj

def map_authors():
    cur = conn.cursor()
    cur.execute(SQL_ALL_AUTHORS)
    num = int(cur.rowcount)
    for idx in range(num):
        row = cur.fetchone()
        print 'Adding Author: name=%s' % (row[2],)
        obj, created = Author.objects.get_or_create(
            name=row[2],
            slug=row[3],
            description=row[4],
            text=row[5],
            email='test_user@unknown.domain.centrum.cz'
        )
        author_map[int(row[0])] = obj

def save_photo(photo_path):
    photo_url = 'http://img.ella.centrum.cz/%s' % photo_path
    target = '%s/static/%s' % (os.getcwd(), photo_path)
    target_dir = os.path.dirname(target)
    downloaded = False
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, 0755)
    if not os.path.exists(target):
        while not downloaded:
            try:
                urllib.urlretrieve(photo_url, target)
                print 'Saved image file %s' % target
                downloaded = True
                sleep(BEFORE_DOWNLOAD_SLEEP)
            except:
                print 'Trying to download image... %s' % photo_url

def map_photos():
    cur = conn.cursor()
    cur.execute(SQL_ARTICLE_IDS)
    cur.execute(SQL_ALL_PHOTOS)
    num = int(cur.rowcount)
    counter = 0
    for idx in range(num):
        counter += 1
        row = cur.fetchone()
        src = None
        if row[6]:
            src = source_map[int(row[6])]
        img_path = row[4]
        print 'Adding Photo: title=%s description=%s image=%s' % (row[1], row[2], img_path)
        if counter % 100 == 0:
            print '*************'
            print ' PHOTO STATUS: %d%%' % int(counter / (num/100.0))
            print '*************'
        save_photo(img_path)
        try:
            obj, created = Photo.objects.get_or_create(
                title=row[1],
                description=row[2],
                slug=row[3],
                image=img_path,
                height=int(row[5]),
                source=src,
                created=row[7]
            )
            photo_map[int(row[0])] = obj.pk
        except:
            print 'Error during saving Photo %s' % img_path

def _map_parent_categories(parent_map):
    cur = conn.cursor()
    tmp = {}
    for old_id in parent_map:
        obj = parent_map[old_id]
        cur.execute(SQL_CHILDREN_CATEGORIES, (old_id,) )
        num = int(cur.rowcount)
        for idx in range(num):
            row = cur.fetchone()
            site_obj = site_map[int(row[6])]
            print 'Adding Category(2): title=%s site=%s tree_path=%s' % (row[1], site_obj, row[4])
            obj, created = Category.objects.get_or_create(
                title=row[1],
                slug=row[2],
                tree_parent=obj,
                #tree_path=row[4],
                description=row[5],
                site=site_obj
            )
            tmp[int(row[0])] = obj
    parent_map.update(tmp)
    return tmp

def map_categories():
    """
    1. Groupnout a ziskat podle tree_parent_id starou tabulku.
    2. Kategorie ziskanych ID vytvorit, ulozit mapovani rodicu stare ID <-> nove ID
    3. Projit vsechny kategorie, premapovat jejich tree_parent_id a ulozit.
    """
    cur = conn.cursor()
    cur.execute(SQL_PARENT_CATEGORIES)
    cur_sec = conn.cursor()
    num = int(cur.rowcount)
    parent_map = {}
    for idx in range(num):
        row = cur.fetchone()
        site_obj = site_map[int(row[6])]
        print 'Adding Category(1): title=%s site=%s tree_path=%s' % (row[1], site_obj, row[4])
        obj, created = Category.objects.get_or_create(
            title=row[1],
            slug=row[2],
            tree_path=row[4],
            description=row[5],
            site=site_obj
        )
        parent_map[int(row[0])] = obj

    _map_parent_categories(parent_map)
    _map_parent_categories(parent_map)
    
    cur.execute(SQL_REMAINING_CATEGORIES)
    num = int(cur.rowcount)
    for idx in range(num):
        row = cur.fetchone()
        site_obj = site_map[int(row[6])]
        print 'Adding Category(3): title=%s site=%s tree_path=%s' % (row[1], site_obj, row[4])
        obj, created = Category.objects.get_or_create(
            title=row[1],
            slug=row[2],
            tree_parent=parent_map[ int(row[3]) ],
            #tree_path=row[4],
            description=row[5],
            site=site_obj
        )
        category_map[int(row[0])] = obj
    category_map.update(parent_map)

def create_content(run_transaction, verbosity, **kwargs):
    global conn
    if run_transaction:
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)
        if verbosity > 1:
            print 'Transaction started'
    conn = mysql.connect(**kwargs)
    # Category, site map tables
    map_sites()
    map_categories()
    map_sources()
    map_photos()
    map_authors()

    # Articles
    cur = conn.cursor()
    cur_sec = conn.cursor()
    cur.execute(SQL_ALL_ARTICLES)
    num = int(cur.rowcount)
    for idx in range(num):
        row = cur.fetchone()
        cat = category_map[int(row[8])]
        id_article = int(row[0])
        print 'Adding Article: title=%s category=%s' % (row[1], cat)
        obj, created = Category.objects.get_or_create(
            title=row[1],
            upper_title=row[2],
            slug=row[3],
            perex=row[4],
            created=row[5],
            updated=row[6],
            source=source_map[int(row[7])],
            category=cat,
            photo=photo_map[int(row[9])]
        )
        cur_sec.execute(SQL_ARTICLE_CONTENTS, (id_article,))
        for xrow in cur_sec.fetchall():
            obj.authors.add( author_map[int(row[2])] )
        article_map[int(row[0])] = obj.pk

    # Article Contents
    map_article_contents()

    # commit changes to database
    if run_transaction:
        transaction.commit()
        #transaction.rollback()
        transaction.leave_transaction_management()
        if verbosity > 1:
            print 'Transaction committed'

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--notransaction', action='store_true', dest='start_transaction',
            help='If specified data insertions won\'t be performed inside transaction.'),
        make_option('--dbuser', dest='dbuser', default='',
            help='Source database user.'),
        make_option('--dbpassword', dest='dbpassword', default='',
            help='Source database password.'),
        make_option('--dbhost', dest='dbhost', default='',
            help='Source database host.'),
        make_option('--dbname', dest='dbname', default='',
            help='Source database name.'),
        make_option('--charencoding', dest='char_encoding', default='utf8',
            help='Source database char fields encoding. (Default utf-8)'),
    )
    help = 'Creates content (moves from old database to the actual. For testing purposes only).'
    args = ""

    def handle(self, *fixture_labels, **options):
        global char_encoding
        verbosity = int(options.get('verbosity', 1))
        run_transaction = not options.get('start_transaction', False)
        kwa = {}
        kwa['user'] = options.get('dbuser')
        kwa['passwd'] = options.get('dbpassword')
        kwa['db'] = options.get('dbname')
        kwa['host'] = options.get('dbhost')
        char_encoding = options.get('char_encoding')
        kwa['charset'] = char_encoding

        create_content(run_transaction, verbosity, **kwa)
