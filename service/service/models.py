import uuid

from django.db import models


class Model(models.Model):
    class Meta:
        abstract = True
        default_permissions = []


class PublicModel(Model):
    public_id = models.UUIDField(
        unique=True,
        editable=False,
        default=uuid.uuid4,
        db_index=True,
    )

    class Meta:
        abstract = True
