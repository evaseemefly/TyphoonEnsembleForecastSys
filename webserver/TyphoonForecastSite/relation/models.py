from django.db import models


# Create your models here.

class RelaTyTaskModel(models.Model):
    ty_id = models.IntegerField(default=-1)  # 台风 id
    task_id = models.IntegerField(default=-1)  # task id
    class Meta:
        db_table = 'rela_ty_task'
