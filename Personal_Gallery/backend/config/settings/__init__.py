"""
Settings package initialization.
Automatically loads the appropriate settings module based on DJANGO_ENV.
"""
import os

# Determine which settings to use
env = os.getenv("DJANGO_ENV", "dev")

if env == "prod":
    from .prod import *
elif env == "dev":
    from .dev import *
else:
    from .base import *