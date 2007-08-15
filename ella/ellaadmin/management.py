from django.contrib import admin
from ella.ellaadmin import site

from ella.articles.models import Article, ArticleOptions

TEXTAREACLASS = 'rich_text_area'
JAVASCRIPTS = [
    'js/prototype.js',
    'js/editor.js',
    'js/showdown.js',
    'js/MagicDOM.js',
]

ArticleOptions.js = JAVASCRIPTS

site.register(Article, ArticleOptions)

print 'MANAGEMENT MANAGEMENT MANAGEMENT'


