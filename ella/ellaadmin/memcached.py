# memcached_status.py
# http://effbot.org/zone/django-memcached-view.htm

import datetime

from django import http
from django.shortcuts import render_to_response
from django.conf import settings

def cache_status(request):

    try:
        import memcache
    except ImportError:
        raise http.Http404('memcache module not found')

    if not (request.user.is_authenticated() and
            request.user.is_superuser):
        return http.HttpResponseForbidden()

    # get first memcached URI
    if not settings.CACHE_BACKEND.startswith('memcached://'):
        raise http.Http404('invalid cache backend')
    cache_hosts = settings.CACHE_BACKEND.split('/')[2]
    cache_hosts = cache_hosts.split(';')

    class Stats:
        pass
    all_stats = []

    for h in cache_hosts:
        host = memcache._Host(h)

        stats = Stats()
        stats.host = '%s:%s' % (host.ip, host.port)

        connected = host.connect()
        if not connected:
            stats.connected = False
            all_stats.append(stats)
            continue

        stats.connected = True
        host.send_cmd("stats")

        while True:
            line = host.readline().split(None, 2)
            if line[0] == "END":
                break

            stat, key, value = line
            try:
                # convert to native type, if possible
                value = int(value)
                if key == "uptime":
                    value = datetime.timedelta(seconds=value)
                elif key == "time":
                    value = datetime.datetime.fromtimestamp(value)
            except ValueError:
                pass
            setattr(stats, key, value)

        stats.hit_rate = 100 * stats.get_hits / stats.cmd_get

        host.close_socket()
        all_stats.append(stats)

    return render_to_response(
        'ellaadmin/memcached_status.html', dict(
            all_stats=all_stats,
            time=datetime.datetime.now(), # server time
    ))
