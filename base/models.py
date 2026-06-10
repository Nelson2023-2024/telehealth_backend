from django.db import models
import uuid

# Create your models here.
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class GenericBaseModel(BaseModel):
    name = models.CharField(blank=True, null=True, max_length=30)
    code = models.CharField(blank=True, null=True, max_length=30)
    description = models.TextField(blank=True, null=True)