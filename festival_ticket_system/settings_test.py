from .settings import *

# Override database configuration for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }
}

# Optional: Disable migrations for faster testing
# MIGRATION_MODULES = {
#     'tickets': None,
#     'auth': None,
#     'contenttypes': None,
#     'sessions': None,
#     'admin': None,
#     'messages': None,
#     'staticfiles': None,
# }