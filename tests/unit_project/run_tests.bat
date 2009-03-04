set PYTHONPATH=..\..;..;.;%PYTHONPATH%
set DJANGO_SETTINGS_MODULE=settings
nosetests --with-django %*
