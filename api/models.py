from django.db import models


class User(models.Model):
    vk_id = models.IntegerField(primary_key=True)
    api_token = models.CharField(max_length=255)


class Project(models.Model):
    user = models.ForeignKey(to=User, related_name='projects')
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
