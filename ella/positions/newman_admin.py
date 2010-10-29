from datetime import datetime

from django import template
from django.conf.urls.defaults import patterns, url
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _, ugettext
from django.shortcuts import render_to_response
from django.contrib.admin import helpers
from django.contrib.contenttypes.models import ContentType

from ella import newman

from ella.positions.models import Position
from ella.core.models import Category
from ella.newman.utils import JsonResponse
from django.forms.models import ModelForm
from django.forms.util import ValidationError

class PositionForm(ModelForm):

    def clean(self):
        cleaned_data = super(PositionForm, self).clean()
        if not self.is_valid():
            return cleaned_data
        if cleaned_data['active_from'] and cleaned_data['active_till']:
            if cleaned_data['active_from'] > cleaned_data['active_till']:
                raise ValidationError(_('Active till must be later than active from.'))
        return cleaned_data

    class Meta:
        model = Position

class PositionAdmin(newman.NewmanModelAdmin):
    form = PositionForm

    list_display = ('name', 'category', 'box_type', 'is_active', 'is_filled', 'show_title', 'disabled',)
    list_filter = ('category', 'disabled', 'active_from', 'active_till',)
    search_fields = ('name', 'box_type', 'text', 'category__title',)

    suggest_fields = {'category': ('__unicode__', 'title', 'slug', 'tree_path',),}

    def show_title(self, obj):
        if not obj.target:
            return '-- %s --' % ugettext('empty position')
        else:
            return u'%s [%s]' % (obj.target.title, ugettext(obj.target_ct.name),)
    show_title.short_description = _('Title')

    def is_filled(self, obj):
        if obj.target:
            return True
        else:
            return False
    is_filled.short_description = _('Filled')
    is_filled.boolean = True

    def is_active(self, obj):
        if obj.disabled:
            return False
        now = datetime.now()
        active_from = not obj.active_from or obj.active_from <= now
        active_till = not obj.active_till or obj.active_till > now
        return active_from and active_till
    is_active.short_description = _('Active')
    is_active.boolean = True


    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^category/(\d+)/$',
                self.positions_by_category_view,
                name='positions-by-category'),
        )
        urlpatterns += super(PositionAdmin, self).get_urls()
        return urlpatterns

    def positions_by_category_view(self, request, category_id, extra_context=None):

        model = self.model
        self.user = request.user

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            # FIXME: redirect
            return HttpResponseRedirect(reverse('newman:index'))

        names = ['featured_secondary_1', 'featured_secondary_2', 'featured_secondary_3', 'poll', 'tipoftheday',
                 'special', 'recipeoftheday', 'featured_small_1', 'featured_small_2',
                 'featured_small_3', ]

        positions = model.objects.filter(category=category_id, name__in=names)

        count = positions.count()

        PositionForm = self.get_form(request)

        if request.method == 'POST':
            forms = [PositionForm(request.POST, prefix=str(positions[x].id),
                                  instance=positions[x]) for x in range(count)]
            if all([form.is_valid() for form in forms]):
                for form in forms:
                    new_object = self.save_form(request, form, change=True)
                    self.save_model(request, new_object, form, change=True)
                    change_message = self.construct_change_message(request, form, None)
                    self.log_change(request, new_object, change_message)

                msg = unicode(_('Positions were changed successfully.'))

                return JsonResponse(msg, data={'category_id': category_id})
        else:
            forms = [PositionForm(prefix=str(positions[x].id),
                                  instance=positions[x]) for x in range(count)]

        adminForms = [helpers.AdminForm(forms[x], self.get_fieldsets(request, positions[x]),
                                self.prepopulated_fields) for x in range(count)]

        errors = []
        for form in forms:
            errors.extend(helpers.AdminErrorList(form, []))

        media = self.media
        if len(adminForms) > 0:
            media += adminForms[0].media

        raw_media = self.prepare_media(media)

        context = {
            'multiple_edit': True,
            'add': False,
            'title': _('Positions in %s') % category.title,
            'category': category,
            'adminforms': adminForms,
            'errors': errors,
            'media': raw_media,
            'is_popup': request.REQUEST.has_key('_popup'),
        }
        context.update(extra_context or {})

        # render change form
        opts = self.model._meta
        app_label = opts.app_label
        ordered_objects = opts.get_ordered_objects()

        context.update({
            'app_label': app_label,
            'change': True,
            'has_add_permission': False,
            'has_change_permission': True,
            'has_delete_permission': False,
            'has_file_field': False,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'ordered_objects': ordered_objects,
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'save_url': reverse('newman:positions-by-category', args=[category_id]),
        })
        return render_to_response("newman/%s/multi_change_form.html" % app_label,
                            context, context_instance=template.RequestContext(request))

newman.site.register(Position, PositionAdmin)
