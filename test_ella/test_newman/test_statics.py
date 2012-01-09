#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.test.client import Client
from django.conf import settings

def test_static():
    c = Client()
    r = c.get('%s/img/nav-bg.gif' % settings.NEWMAN_MEDIA_PREFIX)
    r.status_code == 200
