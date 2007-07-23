from django.core.cache import cache

class CacheDeleter(object):
    def __init__(self):
        self._register = {}

    def __call__(self, sender, instance):
        if sender in self._register:
            for key, test in self._register[sender].items():
                if test(instance):
                    cache.delete(key)
                    del self._register[sender][key]

    def register(self, model, test, key):
        self._register.setdefault(model, {})
        self._register[model][key] = test

CD = CacheDeleter()
