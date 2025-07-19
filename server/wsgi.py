import os
import sys

print("DEBUG: wsgi.py wird geladen", file=sys.stderr)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

print("DEBUG: Vor get_wsgi_application()", file=sys.stderr)
application = get_wsgi_application()
print("DEBUG: Nach get_wsgi_application()", file=sys.stderr)
