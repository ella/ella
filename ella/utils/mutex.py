"""
mutex.py

Ella lock manager
"""

from uuid import uuid1

from django.core.cache import cache

class EllaMutex:
    " EllaMutex(name, lifetime=1800) - create mutex 'name', default lifetime is 30 minutes "
    def __init__(self, name, lifetime=1800):
        self.__key = name
        self.__lifetime = lifetime
        self.__value = uuid1().hex

    def lock(self):
        " lock() - lock mutex, return False if mutex has already locked "
        return cache.add(self.__key, self.__value, self.__lifetime) and True or False

    def unlock(self):
        " unlock() - unlock mutex "
        if self.__status == True:
            cache.delete(self.__key)
            return not self.__status
        return False

    @property
    def __status(self):
        return cache.get(self.__key) == self.__value and True or False
