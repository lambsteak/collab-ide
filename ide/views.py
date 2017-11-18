from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import SiteUser, Project, DiscussionChannel
from .utils import is_logged_in, setup_project


def guestpage(request):
    return render(request, 'ide/guestpage.html')


def login(request):
    member = SiteUser.objects.filter(
        email=request.POST['email'],
        password=request.POST['password']
    )
    if not member:
        return HttpResponse('Invalid username or password')
    member = member[0]
    request.session['m_id'] = member.id
    return redirect('/welcome/')


def signup(request):
    if SiteUser.objects.filter(email=request.POST['email']).exists():
        return HttpResponse('Email already exists')
    if SiteUser.objects.filter(username=request.POST['username']).exists():
        return HttpResponse('Username already exists')
    member = SiteUser.objects.create(
        name=request.POST['name'],
        email=request.POST['email'],
        username=request.POST['username'],
        password=request.POST['password']
    )
    request.session['m_id'] = member.id
    return redirect('/welcome/')


@is_logged_in
def welcome(member, request):
    return render(request, 'ide/welcome.html', context={'member': member})


@is_logged_in
def index(member, request, project_id):
    project = Project.objects.filter(pk=project_id)
    if not project:
        return HttpResponse('The given project does not exist')
    project = project[0]
    if not project.users.filter(id=member.id).exists() and \
            project.admin != member:
        return HttpResponse('You are not authorized to work on this project.')
    context = {}
    context['member'] = member
    context['project'] = project
    context['channel_set'] = project.channels.filter(members__id=member.id)
    return render(request, 'ide/index.html', context)


def default(request):
    m_id = request.session.get('m_id', False)
    if not m_id:
        return redirect('/guestpage/')
    return redirect('/welcome/')


@is_logged_in
def new_project(member, request):
    project_name = request.POST['name']
    if Project.objects.filter(name=project_name).exists():
        return HttpResponse(
            'Project with the same name already exists. Try a different name.')
    project = Project.objects.create(
        name=project_name,
        admin=member,
        token=request.POST['token']
    )
    members = request.POST['project_members'].split(';')
    membs = []
    for memb in members:
        username = memb.strip()
        if SiteUser.objects.filter(username=username):
            if member.username == username:
                continue
            membs.append(SiteUser.objects.get(username=username))
        else:
            return HttpResponse('The given user does not exist')
    project.users.add(*membs)
    # project.users.add(member)
    project.save()
    setup_project(project)
    return redirect('/%d/' % project.id)


@is_logged_in
def join_project(member, request):
    project = Project.objects.filter(name=request.POST['name'])
    if not project:
        return HttpResponse('Project with the given name doesn\'t exist')
    project = project[0]
    if not project.token == request.POST['token']:
        return HttpResponse('Invalid token given for the project')
    project.users.add(member)
    channels = project.channels.filter(for_all_members=True)
    for channel in channels:
        channel.members.add(member)
    project.save()
    return redirect('/%d/' % project.id)


def logout(request):
    if request.session.get('m_id', False):
        del request.session['m_id']
    return redirect('/guestpage/')


@is_logged_in
def dashboard(member, request):
    if request.method == 'GET':
        return render(request, 'ide/dashboard.html', {'member': member})
    return HttpResponse('Notthing happens right now! :p')


@is_logged_in
def new_channel(member, request, project_id):
    if request.method == 'GET':
        project = Project.objects.filter(pk=project_id)
        if not project:
            return HttpResponse('Project does not exist')
        project = project[0]
        return render(request, 'ide/new_channel.html', {'project': project})
    project = Project.objects.filter(pk=project_id)
    if not project:
        return HttpResponse('Project does not exist')
    project = project[0]
    names = request.POST['channel_members'].split(';')
    channel = DiscussionChannel.objects.create(
        project=project,
        name=request.POST['channel_name']
    )
    try:
        channel.members.add(member)
        channel.members.add(*[
            SiteUser.objects.get(username=name.strip()) for name in names
        ])
        channel.save()
    except Exception:
        return HttpResponse('Invalid usernames given')
    return redirect('/%s/' % project_id)
