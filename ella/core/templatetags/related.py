from django import template
from django.db import models
from django.contrib.contenttypes.models import ContentType

from ella.core.cache.utils import get_cached_object
from ella.core.models import Listing, Category

register = template.Library()

class RelatedNode(template.Node):
    def __init__(self, obj_var, count, var_name, mods):
        self.obj_var, self.count, self.var_name, self.models = obj_var, count, var_name, models

    def render(self, context):
        try:
            obj = template.Variable(self.obj_var).resolve(context)
        except template.VariableDoesNotExist:
            return ''

        related = []
        count = self.count

        # manually entered dependencies
        for rel in Related.objects.filter(source_ct=ContentType.objects.get_for_model(obj), source_id=obj._get_pk_val()):
            related.append(rel)
            count -= 1
            if count <= 0:
                break

        # related objects vie tags
        if self.models and count > 0:
            try:
                from tagging.models import TaggedItem
                for m in self.models:
                    to_add = TaggedItem.objects.get_related(obj, m, count)
                    for rel in to_add:
                        if rel != obj and rel not in related:
                            count -= 1
                            related.append(rel)
                        if count <= 0:
                            break
            except ImportError, e:
                pass

        # top objects in given category
        if count > 0:
            cat = get_cached_object(Category, pk=obj.category_id)
            listings = Listing.objects.get_listing(category=cat, count=count, mods=self.models)
            ext = [ listing.target for listing in listings if listing.target != obj ]
            related.extend(ext)
            count -= len(ext)
        if self.all_categories and count > 0:
            listings = Listing.objects.get_listing(count=count, mods=self.models)
            related.extend(listing.target for listing in listings if listing.target != obj)

        context[self.var_name] = related
        return ''

def parse_related_tag(bits):
    if len(bits) < 6:
        raise template.TemplateSyntaxError, "{% related N [app_label.Model, ...] for object as var_name %}"

    if not bits[1].isdigit():
        raise template.TemplateSyntaxError, "Count must be an integer."

    if bits[-2] != 'as':
        raise template.TemplateSyntaxError, "Tag must end with as var_name "
    if bits[-4] != 'for':
        raise template.TemplateSyntaxError, "Tag must end with for object as var_name "

    mods = []
    for m in bits[2:-4]:
        if m == ',':
            continue
        if ',' in m:
            ms = m.split(',')
            for msm in ms:
                if not msm:
                    continue
                try:
                    mods.append(models.get_model(*msm.split('.')))
                except:
                    raise template.TemplateSyntaxError, "%r doesn't represent any model." % msm
        else:
            try:
                mods.append(models.get_model(*m.split('.')))
            except:
                raise template.TemplateSyntaxError, "%r doesn't represent any model." % m

    return bits[-3], int(bits[1]), bits[-1], mods


@register.tag('related')
def do_related(parser, token):
    """
    Get N related models into a context variable.

    Usage::
        {% related N [app_label.Model, ...] for object as var_name %}

    Example::
        {% related 10 for object as related_list %}
        {% related 10 articles.article, galleries.gallery for object as related_list %}
    """
    bits = token.split_contents()
    obj_var, count, var_name, mods = parse_related_tag(bits)
    return RelatedNode(obj_var, count, var_name, mods)



