from django import http

def sample_view(request, bits, context):
    return http.HttpResponse('%s\n%s' % ('/'.join(bits), ','.join('%s:%s' % (key, context[key]) for key in sorted(context.keys()))))

def sample_custom_view(request, context):
    return http.HttpResponse('Sample detail:\n' + ','.join('%s:%s' % (key, context[key]) for key in sorted(context.keys())))

def other_sample_view(request, bits, context):
    return http.HttpResponse()
