from django.db import models


class User(models.Model):
    vk_id = models.IntegerField(primary_key=True)
    api_token = models.CharField(max_length=255)
    exp_token = models.CharField(max_length=255)
