from django.dispatch import Signal

# Signal fired when a Publishable becomes live
content_published = Signal(providing_args=['publishable'])

# and when it's taken down
content_unpublished = Signal(providing_args=['publishable'])
