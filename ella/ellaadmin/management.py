from django.contrib import admin
from ella.ellaadmin import site

from ella.core.models import DependencyOptions
from ella.articles.models import Article, ArticleOptions
from ella.db_templates.models import DbTemplateOptions

TEXTAREACLASS = 'rich_text_area'

JS_PROTOTYPE = 'js/prototype.js'
JS_EDITOR = 'js/editor.js'
JS_SHOWDOWN = 'js/showdown.js'
JS_MAGICDOM = 'js/MagicDOM.js'

JS_GENERIC_LOOKUP = 'js/admin/GenericRelatedObjectLookups.js'
JS_JQUERY = 'js/jquery.js'

ArticleOptions.js = [ JS_PROTOTYPE, JS_EDITOR, JS_SHOWDOWN, JS_MAGICDOM ]
DbTemplateOptions.js = [ JS_JQUERY, JS_GENERIC_LOOKUP ]

#site.register(Article, ArticleOptions)


