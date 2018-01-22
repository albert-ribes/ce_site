"""
WSGI config for ce_site project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../ce_site')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ce_site.settings")

#os.environ['DJANGO_SETTINGS_MODULE'] = 'ce_site.settings'

application = get_wsgi_application()
