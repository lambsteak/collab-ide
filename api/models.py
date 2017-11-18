from django.db import models
from ide.models import SiteUser, Project


class FileEntity(models.Model):
    owner = models.ForeignKey(SiteUser)
    name = models.CharField(max_length=40)
    project = models.ForeignKey(Project, null=True, related_name='files')
    location = models.CharField(max_length=150)
    is_old = models.BooleanField(default=False)

    def __str__(self):
        return self.name + ', ' + self.owner.username


class FileState(models.Model):
    file_entity = models.ForeignKey(FileEntity, related_name='states')
    content = models.TextField()
    owner_comment = models.TextField(null=True)
    other_user_comment = models.TextField(null=True)
    update_on = models.DateTimeField()

    def __str__(self):
        return self.file_entity.name + ', ' + str(self.update_on)
