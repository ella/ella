
from south import *


class Plugins(object):
    def __init__(self):
        self.plugins = {}

    def register(self, app, migration, plugin):
        key = (app, migration)
        if not self.plugins.has_key(key):
            self.plugins[key] = set()
        self.plugins[(app, migration)].add(plugin) 

    def get(self, app, migration):
        return self.plugins.get((app, migration), set())


class SouthPlugin(object):
    @property
    def orm(self):
        return self.migration.orm


plugins = Plugins()

