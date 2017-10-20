from django.db import models


class User(models.Model):
    uid = models.IntegerField()
    sid = models.CharField(max_length=255)
    vk_id = models.IntegerField(primary_key=True)
