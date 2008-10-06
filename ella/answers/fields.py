# -*- coding: iso-8859-1 -*-
# $Id: TimedeltaField.py 101 2008-09-17 13:50:11Z tguettler $
# $HeadURL: svn+ssh://svnserver/svn/djangotools/trunk/dbfields/TimedeltaField.py $

# http://www.djangosnippets.org/snippets/1060/

# Python
import datetime

# Django
from django import forms
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

SECS_PER_DAY=3600*24

class TimedeltaField(models.Field):
    u'''
    Store pythons datetime.timedelta in an integer column.
    Most databasesystems only support 32 Bit integers by default.
    '''
    __metaclass__=models.SubfieldBase
    def __init__(self, *args, **kwargs):
        super(TimedeltaField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if (not value) or isinstance(value, datetime.timedelta):
            return datetime.timedelta(0)
        assert isinstance(value, (int, long,)), (value, type(value))
        return datetime.timedelta(seconds=value)

    def get_internal_type(self):
        return 'IntegerField'

    def get_db_prep_lookup(self, lookup_type, value):
        raise NotImplementedError()  # SQL WHERE

    def get_db_prep_save(self, value):
        if isinstance(value, int):
            return value
        return SECS_PER_DAY*value.days+value.seconds

    def formfield(self, *args, **kwargs):
        return TimedeltaFormField(*args, **kwargs)

class TimedeltaFormField(forms.Field):
    default_error_messages = {
        'invalid':  _(u'Enter a whole number.'),
}
    def __init__(self, *args, **kwargs):
        defaults={'widget': TimedeltaWidget}
        defaults.update(kwargs)
        super(TimedeltaFormField, self).__init__(*args, **defaults)
    def clean(self, value):
        # value comes from Timedelta.Widget.value_from_datadict
        super(TimedeltaFormField, self).clean(value)
        assert len(value)==len(self.widget.inputs), (value, self.widget.inputs)
        i=0
        for value, multiply in zip(value, self.widget.multiply):
            try:
                i+=int(value)*multiply
            except ValueError, TypeError:
                raise forms.ValidationError(self.error_messages['invalid'])
        return i

class TimedeltaWidget(forms.Widget):
    INPUTS=['days', 'hours', 'minutes', 'seconds']
    MULTIPLY=[60*60*24, 60*60, 60, 1]
    def __init__(self, attrs=None):
        self.widgets=[]
        if not attrs:
            attrs={}
        inputs=attrs.get('inputs', self.INPUTS)
        multiply=[]
        for input in inputs:
            assert input in self.INPUTS, (input, self.INPUT)
            self.widgets.append(forms.TextInput(attrs=attrs))
            multiply.append(self.MULTIPLY[self.INPUTS.index(input)])
        self.inputs=inputs
        self.multiply=multiply
        super(TimedeltaWidget, self).__init__(attrs)

    def render(self, name, value, attrs):
        if value is None:
            values=[0 for i in self.inputs]
        elif isinstance(value, datetime.timedelta):
            values=split_seconds(value.days*SECS_PER_DAY+value.seconds, self.inputs, self.multiply)
        elif isinstance(value, int):
            # initial data from model
            values=split_seconds(value, self.inputs, self.multiply)
        else:
            assert isinstance(value, tuple), (value, type(value))
            assert len(value)==len(self.inputs), (value, self.inputs)
            values=value
        id=attrs.pop('id')
        assert not attrs, attrs
        rendered=[]
        for input, widget, val in zip(self.inputs, self.widgets, values):
            rendered.append(u'%s %s' % (input, widget.render('%s_%s' % (name, input), val)))
        return mark_safe('<div id="%s">%s</div>' % (id, ' '.join(rendered)))

    def value_from_datadict(self, data, files, name):
        ret=[]
        for input, multi in zip(self.inputs, self.multiply):
            ret.append(data.get('%s_%s' % (name, input), 0))
        return tuple(ret)

def main():
    assert split_seconds(1000000)==[11, 13, 46, 40]

    field=TimedeltaField()

    td=datetime.timedelta(days=10, seconds=11)
    s=field.get_db_prep_save(td)
    assert isinstance(s, int), (s, type(s))
    td_again=field.to_python(s)
    assert td==td_again, (td, td_again)

    td=datetime.timedelta(seconds=11)
    s=field.get_db_prep_save(td)
    td_again=field.to_python(s)
    assert td==td_again, (td, td_again)

    print "unittest OK"

def split_seconds(secs, inputs=TimedeltaWidget.INPUTS, multiply=TimedeltaWidget.MULTIPLY):
    ret=[]
    for input, multi in zip(inputs, multiply):
        count, secs = divmod(secs, multi)
        ret.append(count)
    return ret

if __name__=='__main__':
    main()
