"""
admin media

usage::
    create web access for admin_media/ directory

    register javascript in newforms admin options
    ella.admin must be on the last position in INSTALLED_APPS

"""

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


