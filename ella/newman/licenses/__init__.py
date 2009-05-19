from django.conf import settings

LICENSED_MODELS = getattr(settings, 'LICENSED_MODELS', ('photos.photo',))
