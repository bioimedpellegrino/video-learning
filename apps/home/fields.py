import json

from django.db import models


class JSONTextField(models.TextField):
    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def to_python(self, value):
        if value in (None, ""):
            return {}
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {}
        return value

    def get_prep_value(self, value):
        if value in (None, ""):
            return json.dumps({})
        if isinstance(value, str):
            return value
        return json.dumps(value)
