import os
from app.settings import *  # noqa

DEBUG = True
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
