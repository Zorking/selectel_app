from django.db import models


class User(models.Model):
    uid = models.IntegerField(primary_key=True)
    sid = models.CharField(max_length=255)
    vk_id = models.CharField(max_length=255)
