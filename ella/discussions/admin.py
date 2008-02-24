from django.contrib import admin

from ella.ellaadmin import widgets
from ella.discussions.models import Question, Topic

class QuestionOptions(admin.ModelAdmin):
    pass

class TopicOptions(admin.ModelAdmin):
    raw_id_fields = ('photo',)
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'perex':
            kwargs['widget'] = widgets.RichTextAreaWidget
        return super(self.__class__, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.register(Question, QuestionOptions)
admin.site.register(Topic, TopicOptions)


