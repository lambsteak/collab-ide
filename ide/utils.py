from django.shortcuts import redirect
from .models import SiteUser
from .models import DiscussionChannel


def is_logged_in(f):
    def decorated_fn(*args, **kwargs):
        request = args[0]
        m_id = request.session.get('m_id', False)
        if not m_id:
            return redirect('/guestpage/')
        member = SiteUser.objects.get(pk=m_id)
        return f(member, *args, **kwargs)
    return decorated_fn


def setup_project(project):
    names = ['Project', 'Issue', 'Misc', 'Meta']
    for name in names:
        channel = DiscussionChannel.objects.create(
            project=project,
            name=name,
            for_all_members=True
        )
        channel.members.add(*[x for x in project.users.all()])
        channel.members.add(project.admin)
        channel.save()
