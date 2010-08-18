"""
Batch command to create all SourceText objects for ella.articles.models.Article and ArticleContents.
ella.articles application has to be installed, otherwise command fails.
"""
from optparse import make_option
import sys

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.contrib.contenttypes.models import ContentType

from djangomarkup.models import SourceText, TextProcessor
from ella.newman import config

def can_run():
    return True

def create_texts(verbosity):
    def update_source(ct, obj, fieldname):
        src, created = SourceText.objects.get_or_create(
            content_type=ct, 
            object_id=obj.pk, 
            field=fieldname,
            processor=default_proc
        )
        if src.content:
            # SourceText already exist for this object
            return
        src.content = getattr(obj, fieldname)
        src.save()
        setattr(obj, fieldname, src.render())
        obj.save()

    from ella.articles.models import Article, ArticleContents
    ct_article = ContentType.objects.get_for_model(Article)
    ct_article_contents = ContentType.objects.get_for_model(ArticleContents)
    markup_name = config.MARKUP_DEFAULT
    if not markup_name:
        sys.stderr.write('No default markup specified. Please set NEWMAN_MARKUP_DEFAULT setting.\n')
        return 
    default_proc = TextProcessor.objects.get(name=markup_name)

    for article in Article.objects.all():
        # article.perex -> SrcText -> Process -> article.perex
        update_source(ct_article, article, 'description')
        contents = ArticleContents.objects.filter(article=article)
        for c in contents:
            # move text to SourceText, process, save back to c.content and c.save()
            update_source(ct_article_contents, c, 'content')
    if verbosity > 0:
        print 'Articles converted to SourceTexts with %s markup.' % markup_name

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--notransaction', action='store_true', dest='start_transaction',
            help='If specified synchronization won\'t be performed inside transaction.'),
    )
    help = 'Batch command to create all SourceText objects for ella.articles.models.Article and ArticleContents.'
    args = ""

    def handle(self, *fixture_labels, **options):
        if not can_run():
            sys.stderr.write('Application ella.articles is not installed. Aborting.\n')
            return

        verbosity = int(options.get('verbosity', 1))
        run_transaction = not options.get('start_transaction', False)
        if run_transaction:
            transaction.commit_unless_managed()
            transaction.enter_transaction_management()
            transaction.managed(True)
            if verbosity > 1:
                print 'Transaction started'
        create_texts(verbosity)

        # commit changes
        if run_transaction:
            transaction.commit()
            transaction.leave_transaction_management()
            if verbosity > 1:
                print 'Transaction committed'

