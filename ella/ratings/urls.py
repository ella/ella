from django.http import Http404

from ella.core.custom_urls import dispatcher
from ella.ratings.views import rate
dispatcher.register('rate',  rate)
