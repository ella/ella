from django import http

def sample_view(request, bits, context):
    return http.HttpResponse('%s\n%s' % ('/'.join(bits), ','.join('%s:%s' % item for item in context.items())))
