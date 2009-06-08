
from south import *

class Plugins(dict):
    
    def register(self, app, migration, plugin):
        key = (app, migration)
        if not key in self:
            self[key] = set()
        self[key].add(plugin)

    def get(self, app, migration):
        return super(Plugins, self).get((app, migration), set())

class SouthPlugin(object):
    @property
    def orm(self):
        return self.migration.orm


plugins = Plugins()

