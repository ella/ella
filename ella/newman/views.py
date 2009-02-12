import logging

from django import template, forms
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import Template
from django.contrib.admin.views.main import ChangeList, ERROR_FLAG
from ella.newman.changelist import NewmanChangeList, FilterChangeList
from django.shortcuts import render_to_response

from ella.newman.options import NewmanModelAdmin


log = logging.getLogger('ella.newman.views')



#NewmanModelAdmin.register(lambda x: x is None, changelist_view)
#NewmanModelAdmin.register(lambda x: x.endswith('filters'), filters_view)
