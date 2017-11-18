from django.db import models


class SiteUser(models.Model):
    username = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=30)
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.username


class Project(models.Model):
    users = models.ManyToManyField(SiteUser)
    name = models.CharField(max_length=40, unique=True)
    admin = models.ForeignKey(SiteUser, related_name='admins')
    token = models.CharField(max_length=70)

    def __str__(self):
        return self.name + ', ' + self.admin.name

    # def save(
    #       self, force_insert=False, force_update=False,
    #        using=None, first_time=False):
    #   if not first_time:
    #        self.users.add(self)
    #   super().save()

    def get_users_names(self):
        for user in self.users.all():
            yield user.name

    def get_channels(self):
        channels = self.channels.all()
        return channels

'''
class Repo(models.Model):
    project = models.ForeignKey(Project, related_name='repos')
    language = models.IntegerField()   # 1: python, 2: c, 3: javascript

    def __str__(self):
        return self.project.name
'''

class Commit(models.Model):
    project = models.ForeignKey(Project, null=True)
    commited_on = models.DateTimeField()
    commited_by = models.ForeignKey(SiteUser)
    state = models.BinaryField()

    def __str__(self):
        return str(self.commited_on) + ' ' + self.commited_by.username


class DiscussionChannel(models.Model):
    project = models.ForeignKey(Project, related_name='channels')
    name = models.CharField(max_length=8)
    members = models.ManyToManyField(SiteUser)
    for_all_members = models.BooleanField(default=False)

    def __str__(self):
        return self.name + ', ' + self.project.name


class DiscussionMessage(models.Model):
    channel = models.ForeignKey(
        DiscussionChannel, related_name='discussion_message_set')
    sender = models.ForeignKey(SiteUser)
    content = models.TextField()
    time = models.DateTimeField()

    def __str__(self):
        return self.content[:30] + '...'

    def save(self, *args, **kwargs):
        self.format_message()
        super().save(*args, **kwargs)

    def format_message(self):
        self.content = self.content.strip()
        self.content = self.content.replace('\n', '<br />')
