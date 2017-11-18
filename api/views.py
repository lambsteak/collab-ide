# from django.shortcuts import render
from django.http import JsonResponse
from ide.models import Project, DiscussionChannel,\
    DiscussionMessage, SiteUser
from .models import FileEntity, FileState
import json
import datetime
# from ide.utils import is_logged_in


def update_state(request, project_id):
    project = Project.objects.filter(pk=project_id)
    if not project:
        resp = {
            'saved_successfully': False,
            'object_not_found': True
        }
        return JsonResponse(resp)
    project = project[0]
    data = json.loads((request.body).decode())
    if data['new_file']:
        name = data['file_name']
        dups = FileEntity.objects.filter(project__id=project_id).\
            exclude(owner__id=data['member_id']).filter(
            name=name, location=data['location'])
        while dups:
            name = name + '*n'
            dups = FileEntity.objects.filter(project__id=project_id).\
                exclude(owner__id=data['member_id']).filter(
                name=name, location=data['location'])
        FileEntity.objects.filter(project__id=project_id).filter(
            owner__id=data['member_id']).filter(
            name=name, location=data['location']).update(is_old=True)
        file_ent = FileEntity.objects.create(
            owner=SiteUser.objects.get(pk=data['member_id']),
            name=name,
            project=project,
            location=data['location']
        )
        data['file_id'] = file_ent.id
    else:
        fid = data['file_id']
        f = FileEntity.objects.get(pk=fid)
        name = f.name
        loc = f.location
        is_dup = False
        dups = FileEntity.objects.filter(project__id=project_id).\
            exclude(owner__id=data['member_id']).filter(
            name=name, location=loc)
        while dups:
            is_dup = True
            name = name + '#'
            dups = FileEntity.objects.filter(project__id=project_id).\
                exclude(owner__id=data['member_id']).filter(
                name=name, location=loc)
        if is_dup:
            second_dup = FileEntity.objects.filter(
                project__id=project_id).filter(
                name=name, owner__id=data['member_id'])
            if not second_dup:
                file_ent = FileEntity.objects.create(
                    owner=SiteUser.objects.get(pk=data['member_id']),
                    name=name,
                    project=project,
                    location=loc
                )
                data['file_id'] = file_ent.id

    filestate = FileState.objects.create(
        file_entity=FileEntity.objects.get(pk=data['file_id']),
        content=data['content'],
        owner_comment=data.get('owner_comment', ''),
        other_user_comment=data.get('other_user_comment', ''),
        update_on=datetime.datetime.now()
    )
    name = FileEntity.objects.get(pk=data['file_id']).name
    loc = FileEntity.objects.get(pk=data['file_id']).location
    resp = {
        'filename': name,
        'location': loc,
        'file_id': data['file_id'],
        'saved_successfully': True,
        'filestate_id': filestate.id
    }
    return JsonResponse(resp)


def fetch_state(request, project_id):
    project = Project.objects.filter(pk=project_id)
    if not project:
        resp = {
            'error': 'Project part of url does not map',
            'fetched_successfully': False,
            'object_not_found': True
        }
        return JsonResponse(resp)
    project = project[0]
    req = json.loads((request.body).decode())
    if req['currently_working_on']:
        filestate = FileState.objects.filter(
            file_entity__owner=req['user_id']).order_by('-update_on')
        if not filestate:
            resp = {
                'error': 'No file state available',
                'fetched_successfully': True,
                'file_found': False
            }
            return JsonResponse(resp)
        filestate = filestate[0]
        resp = {
            'error': 'sending current file',
            'file_found': True,
            'fetched_successfully': True,
            'file_id': filestate.file_entity.id,
            'file_name': filestate.file_entity.name,
            'file_project': filestate.file_entity.project.name,
            'file_location': filestate.file_entity.location,
            'state_content': filestate.content,
            'owner_comment': filestate.owner_comment,
            'other_user_comment': filestate.other_user_comment,
            'update_on': filestate.update_on
        }
        return JsonResponse(resp)
    file_ent = FileEntity.objects.filter(pk=req['file_id'])
    if not file_ent:
        resp = {
            'error': 'File with the given file id not found',
            'fetched_successfully': False,
            'object_not_found': True
        }
        return JsonResponse(resp)
    file_ent = file_ent[0]
    filestate = file_ent.states.all().order_by('-update_on')[0]
    resp = {
        'filename': filestate.file_entity.name,
        'location': filestate.file_entity.location,
        'owner': filestate.file_entity.owner.name,
        'error': 'showing the specified file',
        'file_found': True,
        'fetched_successfully': True,
        'state_content': filestate.content,
        'owner_comment': filestate.owner_comment,
        'other_user_comment': filestate.other_user_comment,
        'update_on': filestate.update_on
    }
    return JsonResponse(resp)


def update_channel(request, project_id):
    project = Project.objects.filter(pk=project_id)
    if not project:
        return JsonResponse({'success': False, 'object_not_found': True})
    project = project[0]
    req = json.loads((request.body).decode())
    channel = DiscussionChannel.objects.get(pk=req['channel_id'])
    messages = channel.discussion_message_set.all().order_by('time')
    resp = {
        'success': True,
        'messages': [
            {
                'sender': m.sender.name,
                'content': m.content,
                'time': m.time.strftime('%B %d, %I:%M %p')
            }
            for m in messages
        ]
    }
    return JsonResponse(resp)


def add_message(request, project_id):
    project = Project.objects.filter(pk=project_id)
    if not project:
        return JsonResponse({'success': False, 'object_not_found': True})
    project = project[0]
    req = json.loads((request.body).decode())
    channel = DiscussionChannel.objects.get(pk=req['channel_id'])
    msg = DiscussionMessage.objects.create(
        channel=channel,
        sender=SiteUser.objects.get(pk=req['user_id']),
        content=req['content'],
        time=datetime.datetime.now()
    )
    return JsonResponse({'success': True, 'message_id': msg.id})


def view_files(request, project_id):
    project = Project.objects.filter(pk=project_id)
    if not project:
        return JsonResponse({
            'success': False,
            'error': 'Project with given id does not exist'
        })
    project = project[0]
    files = []
    oldfiles = []
    for fl in project.files.filter(is_old=False).order_by('-id'):
        l = []
        l.append(fl.location)
        l.append(fl.name)
        l.append(fl.owner.name)
        last_mod = fl.states.all().order_by('-update_on')[0].update_on
        l.append(last_mod.strftime('%b %d, %H:%M'))
        l.append(fl.id)
        files.append(l)
    for fl in project.files.filter(is_old=True).order_by('-id'):
        l = []
        l.append(fl.location)
        l.append(fl.name)
        l.append(fl.owner.name)
        last_mod = fl.states.all().order_by('-update_on')[0].update_on
        l.append(last_mod.strftime('%b %d, %H:%M'))
        l.append(fl.id)
        oldfiles.append(l)
    oldpresent = False
    if oldfiles:
        oldpresent = True
    return JsonResponse({
        'success': True,
        'files': files,
        'oldfiles': oldfiles,
        'oldfiles_present': oldpresent
    })
    '''[
        ['home', 'file1.c', 'pp', '2017', 1],
        ['root', 'file2.c', 'abc', '2016', 2]
    ]'''
