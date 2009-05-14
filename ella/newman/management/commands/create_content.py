# -*- coding: UTF-8 -*-
"""
Dirty command to get old structurred data from db 'ella'.
"""
from optparse import make_option
import urllib
import os, os.path
import shutil
import sys
import MySQLdb as mysql
from time import sleep

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.contrib.sites.models import Site

from ella.core.models import Category, Author, Source, Placement, Listing
from ella.newman.models import CategoryUserRole, DenormalizedCategoryUserRole
from ella.articles.models import Article, ArticleContents
from ella.photos.models import Photo

NO_VERB = 0
STD_VERB = 1
HIGH_VERB = 2
BEFORE_DOWNLOAD_SLEEP = 0.02
PHOTO_STATUS_MOD = 500  # photo import status mod.

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

# Get models ct_id
SQL_CONTENT_TYPE = """
SELECT
    id,
    name,
    app_label,
    model
FROM
    django_content_type
WHERE
    app_label = %s
    AND
    model = %s
"""

# Article's placement
SQL_PLACEMENT = """
SELECT
    id,
    target_ct_id,
    target_id,
    category_id,
    publish_from,
    publish_to,
    slug,
    static
FROM
    core_placement
WHERE
    target_ct_id = %s
    AND
    target_id = %s
"""

# Article's listings
SQL_LISTINGS = """
SELECT
    id,
    placement_id,
    category_id,
    publish_from,
    priority_from,
    priority_to,
    priority_value,
    remove,
    commercial
FROM
    core_listing
WHERE
    placement_id = %s
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

conn = None # global variable holds connection to database
verbosity = None # holds command's verbosity level
img_url_prefix = None

site_map = {}     # key .. old ID, value .. new Site 
category_map = {} # key .. old ID, value .. new Category
char_encoding = None
source_map = {}
photo_map = {}
article_map = {}
author_map = {}

def printv(text, verb=HIGH_VERB):
    if verb <= verbosity:
        print text

def set_default_socket_timeout(tout):
    import socket
    socket.setdefaulttimeout(tout)
    printv('Socket timeout set to %d sec.' % tout, STD_VERB)

def map_sites():
    cur = conn.cursor()
    cur.execute(SQL_ALL_SITES)
    num = int(cur.rowcount)
    for idx in xrange(num):
        row = cur.fetchone()
        if row[2]:
            printv( 'Adding Site: domain=%s name=%s' % (row[1], row[2]))
            obj, created = Site.objects.get_or_create(domain=row[1], name=row[2])
            site_map[int(row[0])] = obj
    printv('Sites done.', STD_VERB)

def map_article_contents():
    cur = conn.cursor()
    cur.execute(SQL_ALL_ARTICLE_CONTENTS)
    num = int(cur.rowcount)
    for idx in xrange(num):
        if idx % PHOTO_STATUS_MOD == 0:
            progress('ArticleContents import', int(idx / (num/100.0)))
        row = cur.fetchone()
        old_id = int(row[1])
        if old_id not in article_map:
            continue
        printv( 'Adding A.Contents: title=%s' % (row[2],))
        obj, created = ArticleContents.objects.get_or_create(
            title=row[2],
            content=row[3],
            article=article_map[old_id]
        )
    printv('ArticleContents done.', STD_VERB)

def progress(msg, perc):
    printv('********************')
    printv(' %s: %d%%' % (msg, perc), STD_VERB)
    printv('********************')

def map_sources():
    cur = conn.cursor()
    cur.execute(SQL_ALL_SOURCES)
    num = int(cur.rowcount)
    for idx in xrange(num):
        row = cur.fetchone()
        printv('Adding Source: name=%s url=%s' % (row[1], row[2]))
        obj, created = Source.objects.get_or_create(name=row[1], url=row[2], description=row[3])
        source_map[int(row[0])] = obj
    printv('Sources done.', STD_VERB)

def map_authors():
    cur = conn.cursor()
    cur.execute(SQL_ALL_AUTHORS)
    num = int(cur.rowcount)
    counter = 0
    for idx in xrange(num):
        counter += 1
        row = cur.fetchone()
        printv('Adding Author: name=%s' % (row[2],))
        try:
            obj, created = Author.objects.get_or_create(
                name=row[2],
                slug='%s-%03d' % (row[3], counter),  # counter added due to problems with slug uniqueness
                description=row[4],
                text=row[5],
                email='test_user.%03d@unknown.domain.centrum.cz' % counter
            )
            author_map[int(row[0])] = obj
        except:
            printv('! Cannot create author: %s' % row[2], NO_VERB)
            # map to different author
            author_map[int(row[0])] = Author.objects.all()[0]
    printv('Authors done.', STD_VERB)

def save_photo(photo_path):
    def cback(arg, dirname, fnames):
        for f in fnames:
            if f.endswith(arg):
                shutil.copyfile('%s/%s' %(dirname, f), '%s/%s' % (dirname, arg))
                break

    def process_formatted(fpath):
        if os.path.exists(fpath):
            return #better safe than sorry
        fname = os.path.basename(fpath)
        os.path.walk(os.path.dirname(fpath), cback, fname)

    photo_url = '%s%s' % (img_url_prefix, photo_path)
    target = '%s/static/%s' % (os.getcwd(), photo_path)
    target_dir = os.path.dirname(target)
    downloaded = False
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, 0755)
    process_formatted(target) # copies existing photo to original filename (it may lead to wrong-sized photos)
    if not os.path.exists(target):
        while not downloaded:
            try:
                urllib.urlretrieve(photo_url, target)
                printv('Saved image file %s' % target)
                downloaded = True
                sleep(BEFORE_DOWNLOAD_SLEEP)
            except:
                printv('Trying to download image... %s' % photo_url)

def map_photos():
    cur = conn.cursor()
    cur.execute(SQL_ARTICLE_IDS) # create temp. table rather than inner query (inner query is too slow on mysql)
    cur.execute(SQL_ALL_PHOTOS)
    num = int(cur.rowcount)
    for idx in xrange(num):
        row = cur.fetchone()
        src = None
        if row[6]:
            src = source_map[int(row[6])]
        img_path = row[4]
        if idx % PHOTO_STATUS_MOD == 0:
            progress('Photo import', int(idx / (num/100.0)))
        counter += 1
        existing = Photo.objects.filter(
            title=row[1],
            description=row[2],
            slug=row[3],
            source=src
        )
        if existing:
            # Photo is present in database
            photo_map[int(row[0])] = existing[0]
            continue
        printv('Adding Photo: title=%s description=%s image=%s' % (row[1], row[2], img_path))
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
            photo_map[int(row[0])] = obj
        except Exception, e:
            printv('! Error during saving Photo %s, %s' % (img_path, str(e)), NO_VERB)
    printv('Photos done.', STD_VERB)

def save_photo_map(fname='/tmp/photo_map'):
    fp = file(fname, 'w')
    for key in photo_map:
        fp.write('%d:%d\n' % (key, photo_map[key].pk))
    fp.close()

def load_photo_map(fname='/tmp/photo_map'):
    fp = file(fname, 'r')
    line = fp.readline()
    while line:
        line = line.strip()
        orig_id, exist_id = line.split(':')
        photo_map[int(orig_id)] = Photo.objects.get(pk=int(exist_id))
        line = fp.readline()
    fp.close()
    printv('Photo map loaded. %d' % len(photo_map), STD_VERB)


def _map_parent_categories(parent_map):
    cur = conn.cursor()
    tmp = {}
    for old_id in parent_map:
        obj = parent_map[old_id]
        cur.execute(SQL_CHILDREN_CATEGORIES, (old_id,) )
        num = int(cur.rowcount)
        for idx in xrange(num):
            row = cur.fetchone()
            site_obj = site_map[int(row[6])]
            printv('Adding Category(2): title=%s site=%s tree_path=%s' % (row[1], site_obj, row[4]))
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
    # FIXME ugly procedure, refactor someday
    cur = conn.cursor()
    cur.execute(SQL_PARENT_CATEGORIES)
    cur_sec = conn.cursor()
    num = int(cur.rowcount)
    parent_map = {}
    for idx in xrange(num):
        row = cur.fetchone()
        site_obj = site_map[int(row[6])]
        printv('Adding Category(1): title=%s site=%s tree_path=%s' % (row[1], site_obj, row[4]))
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
    for idx in xrange(num):
        row = cur.fetchone()
        site_obj = site_map[int(row[6])]
        printv('Adding Category(3): title=%s site=%s tree_path=%s' % (row[1], site_obj, row[4]))
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
    printv('Categories done.', STD_VERB)

def map_articles():
    cur = conn.cursor()
    cur_sec = conn.cursor()
    cur.execute(SQL_ALL_ARTICLES)
    num = int(cur.rowcount)
    for idx in xrange(num):
        if idx % PHOTO_STATUS_MOD == 0:
            progress('Article import', int(idx / (num/100.0)))
        row = cur.fetchone()
        cat = category_map[int(row[8])]
        id_article = int(row[0])
        printv('Adding Article: title=%s category=%s' % (row[1], cat))
        kwargs = {
            'title': row[1],
            'upper_title': row[2],
            'slug': row[3],
            'description': row[4],
            #'created': row[5],
            #'updated': row[6],
            'category': cat,
        }
        if row[9] and row[9] in photo_map:
            kwargs['photo'] = photo_map[int(row[9])]
        if row[7] and row[7] in source_map:
            kwargs['source'] = source_map[int(row[7])],
        try:
            obj, created = Article.objects.get_or_create(**kwargs)
            cur_sec.execute(SQL_ARTICLE_AUTHORS, (id_article,))
            for xrow in cur_sec.fetchall():
                obj.authors.add( author_map[int(xrow[2])] )
            article_map[int(row[0])] = obj
        except:
            printv('! Problem during creation of Article id=%d title=%s' % (row[0], row[1]), NO_VERB)
    printv('Articles done. Total articles: %d' % Article.objects.all().count(), STD_VERB)

def create_placements():
    """
    1. najit CT modelu Article ve stare db
    2. najit placement pro kazdy z mapovanych clanku (podle old CT a mapovaneho ID clanku)
    3. vlozit placement
    4. pro old placement id nalezt listingy, vlozit k novemu placement id
    """
    cur = conn.cursor()
    cur_lst = conn.cursor()
    cur.execute(SQL_CONTENT_TYPE, (Article._meta.app_label, Article._meta.verbose_name_raw.lower(),))
    row = cur.fetchone()
    old_ct_id = row[0]
    for old_article_id in article_map:
        art = article_map[old_article_id]
        cur.execute(SQL_PLACEMENT, (old_ct_id, old_article_id))
        for row in cur.fetchall():
            old_placement_id = row[0]
            plac, created = Placement.objects.get_or_create(
                publishable=art,
                category=art.category,
                publish_from=row[4],
                publish_to=row[5],
                slug=row[6],
                static=row[7]
            )
            cur_lst.execute(SQL_LISTINGS, (old_placement_id,))
            for lst in cur_lst.fetchall():
                obj, created = Listing.objects.get_or_create(
                    placement=plac,
                    category=category_map[lst[2]],
                    publish_from=lst[3],
                    priority_from=lst[4],
                    priority_to=lst[5],
                    priority_value=lst[6],
                    commercial=lst[8]
                )

def create_content(run_transaction, verbosity, **kwargs):
    global conn
    if run_transaction:
        transaction.commit_unless_managed()
        transaction.enter_transaction_management()
        transaction.managed(True)
        printv('Transaction started')
    conn = mysql.connect(**kwargs)
    # Category, site map tables
    map_sites()
    map_categories()
    map_sources()
    
    #map_photos() # temporarily commented out
    #save_photo_map() 
    load_photo_map()
    map_authors()

    # Articles
    map_articles()
    # Placements
    create_placements()

    # Article Contents
    map_article_contents()

    # commit changes to database
    if run_transaction:
        transaction.commit()
        #transaction.rollback()
        transaction.leave_transaction_management()
        printv('Transaction committed')

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
        make_option('--timeout', dest='sock_timeout', default='10',
            help='Default socket timeout. Affects timeouts when downloading Photos.'),
        make_option('--charencoding', dest='char_encoding', default='utf8',
            help='Source database char fields encoding. (Default utf-8)'),
        make_option('--urlprefix', dest='url_prefix', default='http://img.ella.centrum.cz/',
            help='URL prefix to be used when downloading photos.'),
    )
    help = 'Creates content (moves from old database to the actual. For testing purposes only).'
    args = ""

    def handle(self, *fixture_labels, **options):
        global char_encoding, verbosity, img_url_prefix 
        verbosity = int(options.get('verbosity', 1))
        run_transaction = not options.get('start_transaction', False)
        kwa = {}
        kwa['user'] = options.get('dbuser')
        kwa['passwd'] = options.get('dbpassword')
        kwa['db'] = options.get('dbname')
        kwa['host'] = options.get('dbhost')
        char_encoding = options.get('char_encoding')
        timeout = int(options.pop('sock_timeout'))
        IMG_URL_PREFIX = options.pop('url_prefix')
        kwa['charset'] = char_encoding

        if not (kwa['user'] and kwa['db'] and kwa['host']):
            print 'Please specify at least command parameters --dbuser, --dbname and --dbhost.'
            sys.exit(1)

        set_default_socket_timeout(timeout)
        create_content(run_transaction, verbosity, **kwa)
