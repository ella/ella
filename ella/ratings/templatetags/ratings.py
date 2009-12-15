from decimal import Decimal

from django import template
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from ella.ratings.models import TotalRate
from ella.ratings.forms import RateForm
from ella.ratings.views import get_was_rated
from django.utils.translation import ugettext as _

from recepty import settings

register = template.Library()

DOUBLE_RENDER = getattr(settings, 'DOUBLE_RENDER', False)

#class RateUrlsNode(template.Node):
#    def __init__(self, object, up_name, down_name, form_name=None):
#        self.object, self.up_name, self.down_name = object, up_name, down_name
#        self.form_name = form_name
#
#    def render(self, context):
#        obj = template.Variable(self.object).resolve(context)
#        if obj and hasattr(obj, 'get_absolute_url'):
#            context[self.up_name] = '%s%s/%s/' % (obj.get_absolute_url(), _('rate'), _('up'))
#            context[self.down_name] = '%s%s/%s/' % (obj.get_absolute_url(), _('rate'), _('down'))
#        elif obj:
#            ct = ContentType.objects.get_for_model(obj)
#            context[self.form_name] = RateForm(initial={'content_type' : ct.id, 'target' : obj._get_pk_val()})
#            context[self.up_name] = reverse('rate_up')
#            context[self.down_name] = reverse('rate_down')
#        return ''

class RateUrlNode(template.Node):
    def __init__(self, object, url_var_name, form_name=None):
        self.object = object
        self.url_var_name =url_var_name
        self.form_name = form_name

    def render(self, context):
        obj = template.Variable(self.object).resolve(context)
        if obj and hasattr(obj, 'get_absolute_url'):
            context[self.url_var_name] = '%s%s/' % (obj.get_absolute_url(), slugify(_('rate')))
        elif obj:
            ct = ContentType.objects.get_for_model(obj)
            context[self.form_name] = RateForm(initial={'content_type' : ct.id, 'target' : obj._get_pk_val()})
            context[self.url_var_name] = reverse('rate')
        return ''

#@register.tag('rate_urls')
#def do_rate_urls(parser, token):
#    """
#    Generate absolute urls for rating the given model up or down and store them in context.
#
#    Usage::
#
#        {% rate_urls for OBJ as var_up var_down %}
#
#        {% rate_urls for OBJ as my_form var_up var_down %}
#
#    Examples::
#
#        {% rate_urls for object as url_up url_down %}
#        <form action="{{url_up}}" method="POST"><input type="submit" value="+"></form>
#        <form action="{{url_down}}" method="POST"><input type="submit" value="-"></form>
#
#        {% rate_urls for object as rate_form url_up url_down %}
#        <form action="{{url_up}}" method="POST">{{rate_form}}<input type="submit" value="+"></form>
#        <form action="{{url_down}}" method="POST">{{rate_form}}<input type="submit" value="-"></form>
#    """
#    bits = token.split_contents()
#    if (len(bits) != 6 and len(bits) != 7) or bits[1] != 'for' or bits[3] != 'as':
#        raise template.TemplateSyntaxError, "%r .... TODO ....." % token.contents.split()[0]
#    if len(bits) == 6:
#        return RateUrlsNode(bits[2], bits[4], bits[5])
#    else:
#        return RateUrlsNode(bits[2], bits[5], bits[6], bits[4])

@register.tag
def rate_url(parser, token):
    """
    Fills template variable specified in argument ``tpl_var`` with URL for sending rating value.

    Usage::

        {% rate_url for object as tpl_var %}

    Example::

        {% rate_url for object as r_url %}
        <form action="{{r_url}}" method="POST">
            <input type="text" name="rating" value="0"/>
            <input type="submit" value="Rate it"/>
        </form>
    """
    bits = token.split_contents()
    if len(bits) != 5:
        raise template.TemplateSyntaxError('rate_rul template tag should be used like this: {% rate_url for object as tpl_var %}')
    return RateUrlNode(bits[2], bits[4])

class RatingNode(template.Node):
    def __init__(self, object, name, max=None, step=None, min2=None):
        self.object, self.name = object, name
        self.min, self.max, self.step, self.min2 = min, max, step, min2

    def render(self, context):
        obj = template.Variable(self.object).resolve(context)
        if obj:
            value = 0
            if (self.min != None and self.max!=None and self.min2 != None):
                self.step = Decimal(self.step)
                self.min2 = Decimal(self.min2)
                self.max = Decimal(self.max)
                possible_values = int((self.max - self.min2)/self.step+1)
                value = TotalRate.objects.get_normalized_rating(obj, 1, Decimal("1.0")/(possible_values/2))
                value = value*(self.max - self.min2)/2 + (self.max+self.min2)/2

                # Due to the nature of the 'get_normalized_rating' function, an odd number
                # of possible return values is required. If the input parameters yield
                # an even number of possible return values, an approximation is necessary.
                #
                # In the following cycle, the value closest to the obtained result still
                # fulfilling the input 'min', 'max' and 'step' parameters is being looked for.

                if possible_values%2 == 0:
                    old_value = self.min2
                    best_approximation = self.min2
                    while (1):
                        cur_value = old_value + self.step
                        if cur_value > self.max:
                            break
                        old_error = abs(old_value - value)
                        cur_error = abs(cur_value - value)
                        if cur_error <= old_error:
                            best_approximation = cur_value
                        elif cur_error >= best_approximation:
                            break
                        old_value = cur_value
                    value = best_approximation

            elif (self.min is not None and self.max is not None):
                value = TotalRate.objects.get_normalized_rating(obj, Decimal(self.max), Decimal(self.step))
            else:
                value = TotalRate.objects.get_total_rating(obj)
            # Set as string to be able to compare value in template
            context[self.name] = str(value)
        return ''

@register.tag('rating')
def do_rating(parser, token):
    """
    Get rating for the given object and store it in context under given name.

    Usage::
        Select total rating:
        {% rating for OBJ as VAR %}

        Normalize rating to <-X, X> with step Y and round to Z:
        {% rating for OBJ max X step Y as VAR %}

        Normalize rating to <X, Y> with step S:
        {% rating for OBJ min X max Y step S as VAR %}

            Notice:

                In order to obtain correct results, (Y-X)/S must be in Z (integers).

                Also, (Y-X)/S+1 (number of possible values the function can return)
                should preferably be an odd number, as it better corresponds to
                the way the 'get_normalized_rating' function works.

    Examples::

        {% rating for object as object_rating %}
        object {{object}} has rating of {{object_rating}}

        {% rating for object max 1 step 0.5 as object_rating %}
        object {{object}} has rating of {{object_rating}} from (-1, -0.5, 0, 0.5, 1)

    """
    bits = token.split_contents()
    if len(bits) == 5 and bits[1] == 'for' and bits[3] == 'as':
        return RatingNode(bits[2], bits[4])
    if len(bits) == 9 and bits[1] == 'for' and bits[3] == 'max' \
            and bits[5] == 'step' and bits[7] == 'as':
        return RatingNode(bits[2], bits[8], bits[4], bits[6])
    if len(bits) == 11 and bits[1] == 'for' and bits[3] == 'min' \
            and bits[5] == 'max' and bits[7] == 'step' and bits[9] == 'as':
        return RatingNode(bits[2], bits[10], bits[6], bits[8], bits[4])

    raise template.TemplateSyntaxError, \
        "{% rating for OBJ as VAR %} or {% rating for OBJ max X step Y as VAR %}"

class WasRatedNode(template.Node):

    def __init__(self, object, name):
        self.object, self.name = object, name

    def render(self, context):
        object = template.Variable(self.object).resolve(context)
        ct = ContentType.objects.get_for_model(object)
        context[self.name] = get_was_rated(context['request'], ct, object)
        return ''

@register.tag('was_rated')
def do_was_rated(parser, token):
    """
    {% was_rated for OBJ as VAR %}
    """
    bits = token.split_contents()
    if len(bits) == 5 and bits[1] == 'for' and bits[3] == 'as':
        return WasRatedNode(bits[2], bits[4])
    raise template.TemplateSyntaxError, "{% was_rated for OBJ as VAR %}"


class TopRatedNode(template.Node):
    def __init__(self, count, name, mods=None):
        self.count, self.name, self.mods = count, name, mods

    def render(self, context):
        # FIXME: remove try-except after rating migration
        try:
            context[self.name] = TotalRate.objects.get_top_objects(self.count, self.mods)
        except:
            pass
        return ''

@register.tag('top_rated')
def do_top_rated(parser, token):
    """
    Get list of COUNT top rated objects of given model and store them in context under given name.

    Usage::

        {% top_rated 5 [app.model ...] as var %}

    Example::

        {% top_rated 10 as top_rated_objects %}
        {% for obj in top_rated_objects %}   ...   {% endfor %}

        {% top_rated 10 articles.article as top_articles %}
        {% for article in top_articles %}   ...   {% endfor %}

        {% top_rated 10 articles.article photos.photo as top_objects %}
        {% for obj in top_objects %}   ...   {% endfor %}
    """
    bits = token.split_contents()
    if len(bits) < 3 or bits[-2] != 'as':
        raise template.TemplateSyntaxError, "%r .... TODO ....." % token.contents.split()[0]

    count = int(bits[1])


    mods = []
    for mod in bits[2:-2]:
        model = models.get_model(*mod.split('.', 1))
        if not model:
            raise template.TemplateSyntaxError, "%r .... TODO ....." % token.contents.split()[0]
        mods.append(model)

    return TopRatedNode(count, bits[-1], mods)

class IfWasRatedNode(template.Node):

    def __init__(self, nodelist_true, nodelist_false, obj=None, ct=None, pk=None):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.obj= None
        if obj:
            self.obj = template.Variable(obj)
        self.ct = ct
        self.pk = pk

    def render(self, context):

        if self.obj:
            obj = self.obj.resolve(context)
            ct = ContentType.objects.get_for_model(obj).id
            pk = obj.pk
        else:
            ct = self.ct
            pk = self.pk

        if DOUBLE_RENDER and 'SECOND_RENDER' not in context:
            return u"{%% load ratings %%}" \
                   u"{%% if_was_rated %(ct)s:%(pk)s %%}" \
                   u"%(nodelist_true)s{%% else %%}%(nodelist_false)s{%% endif_was_rated %%}" % ({
                            'ct' : ct,
                            'pk' : pk,
                            'nodelist_true' : self.nodelist_true.render(context),
                            'nodelist_false' : self.nodelist_false.render(context),
                    })

        if get_was_rated(context['request'], ct, pk):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


@register.tag('if_was_rated')
def do_if_was_rated(parser, token):
    """
    {% if_was_rated object %}...{% else %}...{% endif_was_rated %}
    """
    bits = token.contents.split()

    if len(bits) == 2:
        kwargs = {}
        # Opening tag
        obj = bits[1]
        if ":" in obj:
            ct,pk = obj.split(":")
            kwargs.update({"ct":int(ct), "pk":int(pk)})
        else:
            kwargs.update({"obj":obj})
        # Nodelist true
        nodelist_true = parser.parse(('else', 'endif_was_rated'))
        token = parser.next_token()
        kwargs.update({"nodelist_true":nodelist_true})
        # Nodelist false
        if token.contents == 'else':
            nodelist_false = parser.parse(('endif_was_rated',))
            kwargs.update({"nodelist_false":nodelist_false})
            parser.delete_first_token()
        else:
            nodelist_false = template.NodeList()
        return IfWasRatedNode(**kwargs)

    raise template.TemplateSyntaxError, "{%% %s object %%}" % bits[0]
