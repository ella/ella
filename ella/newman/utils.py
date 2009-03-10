try:
    import cjson
    dumps = cjson.encode
    loads = cjson.decode
except ImportError:
    from django.utils.simplejson import dumps, loads


def json_encode(data):
    """ Encode python data into JSON. Try faster cjson first. """

    return dumps(data)

def json_decode(str):
    """ Decode JSON string into python. """

    return loads(str)
