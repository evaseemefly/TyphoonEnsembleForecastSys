from django.db import models


# Create your models here.
class IDictModel(models.Model):
    '''
        所有字典表的抽象父类
    '''
    # id=models.AutoField
    code = models.IntegerField(default=-1, primary_key=True)
    pid = models.IntegerField(default=-1)
    # type_code = models.CharField(max_length=20)
    # name = models.CharField(max_length=20)
    desc = models.CharField(max_length=200)
    val = models.CharField(max_length=50)

    class Meta:
        abstract = True


class DictBaseModel(IDictModel):
    class Meta:
        db_table = 'common_dict'
