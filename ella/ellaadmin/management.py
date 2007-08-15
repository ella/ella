from django.contrib import admin


TEXTAREACLASS = 'rich_text_area'
JAVASCRIPTS = [
    'js/prototype.js',
    'js/editor.js',
    'js/showdown.js',
    'js/MagicDOM.js',
]


class EllaAdminSite(admin.AdminSite):
    pass

site = EllaAdminSite()

from ella.articles.models import Article, ArticleOptions
ArticleOptions.js = JAVASCRIPTS

site.register(Article, ArticleOptions)

