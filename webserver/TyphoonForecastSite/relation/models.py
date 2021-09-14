from django.db import models
from util.const import UNLESS_CELERY_ID


# Create your models here.

class RelaTyTaskModel(models.Model):
    ty_id = models.IntegerField(default=-1)  # 台风 id
    celery_id = models.CharField(default=UNLESS_CELERY_ID, max_length=100)  # celery id

    class Meta:
        db_table = 'rela_ty_task'
