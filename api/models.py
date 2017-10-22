from django.db import models

from api.utils.servers import authenticate_project, get_projects, get_region


class User(models.Model):
    vk_id = models.IntegerField(primary_key=True)
    api_token = models.CharField(max_length=255)
    token = models.CharField(max_length=1024)

    def create__or_update_projects(self):
        for project in get_projects(self.api_token):
            proj, _ = Project.objects.update_or_create(project_id=project.get('id'),
                                                       defaults={
                                                           'user': self, 'name': project.get('name'),
                                                           'region_name': get_region(project.get('id'),
                                                                                     self.api_token)})
            proj.update_auth()


class Project(models.Model):
    project_id = models.CharField(max_length=255, primary_key=True)
    region_name = models.CharField(max_length=255, default='ru-1')
    user = models.ForeignKey(to=User, related_name='projects')
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, null=True)

    def update_auth(self):
        token = authenticate_project(self.project_id, self.user.api_token)
        if token:
            self.token = token
            self.save()
