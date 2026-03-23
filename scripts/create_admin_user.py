import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from django.contrib.auth import get_user_model


User = get_user_model()
user, created = User.objects.get_or_create(
    username="admin",
    defaults={
        "email": "admin@example.com",
        "is_staff": True,
        "is_superuser": True,
    },
)
user.is_staff = True
user.is_superuser = True
user.email = user.email or "admin@example.com"
user.set_password("admin")
user.save()

print("created" if created else "updated")
