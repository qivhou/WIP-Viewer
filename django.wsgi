import os
import sys
import django.core.handlers.wsgi

sys.path.append(r'D:/Python')
sys.path.append(r'D:/Python/djangosite')
os.environ['DJANGO_SETTINGS_MODULE'] = 'djangosite.settings'
application = django.core.handlers.wsgi.WSGIHandler()