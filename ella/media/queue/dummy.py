"""
trivial pseudo queue mechanism - only for debugging and some devel purposes

it import registered function, runs it imediatelly after recieving a signal
and waits until it is finished


it should work like this::

>>> q = DummyQueue()
>>> q.register('PRINT', 'pprint.pprint')
>>> q.put('PRINT', 'a')
'a'

>>> q.register('PRINT', 'sys.stdout.write')
>>> q.put('PRINT', 'b')
'b'
b

# create some nested callable object
>>> class A(object):
...    class B:
...        class C:
...            @staticmethod
...            def f(x):
...                print x

>>> import ella
>>> ella.X = A

>>> q.register('PRINT', 'ella.X.B.C.f')
>>> q.put('PRINT', 'aaa')
'aaa'
aaaaaa

# there is no such callable object
>>> q.register('XXXXX', 'a.b.c.d.e')
>>> q.put('XXXXX', 'aaa')

"""


class DummyQueue(object):
    def __init__(self):
        self.listeners = {}
        self.cache = {}

    def str_import(self, listener):
        """import module and get function object from it"""
        if listener in self.cache:
            return self.cache[listener]
        func = str_import(listener)
        self.cache[listener] = func
        return func

    def put(self, origin, item):
        """find all registered listeners and pass them item parameter"""
        listeners = self.listeners.get(origin, [])
        for listener in listeners:
            listener(item)

    def register(self, onwhat, listener):
        """register function that will be imported and called on put()"""
        if isinstance(listener, basestring):
            listener = self.str_import(listener)
        if callable(listener):
            if onwhat in self.listeners:
                self.listeners[onwhat].append(listener)
            else:
                self.listeners[onwhat] = [listener]

def str_import(i_str):
    """helper function that load object from submodule"""
    i_list = i_str.split('.')

    x = None
    i = len(i_list) + 1
    while not x and i > 1:
        i -= 1
        try:
            x = __import__('.'.join(i_list[:i]), {}, {}, [''])
        except ImportError:
            continue

    if not x:
        x = __builtins__

    for j in i_list[i:]:
        try:
            x = getattr(x, j)
        except AttributeError:
            return None

    return x

