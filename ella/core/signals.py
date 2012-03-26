from django.dispatch import Signal

# Signal fired when a Publishable becomes live
content_published = Signal(providing_args=['publishable'])

# and when it's taken down
content_unpublished = Signal(providing_args=['publishable'])

# category or publishable is about to be rendered
object_rendering = Signal(providing_args=['request', 'category', 'publishable'])

# category or publishable was rendered
object_rendered = Signal(providing_args=['request', 'category', 'publishable'])
