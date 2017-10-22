from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.auth import VkAuthentication
from api.models import User, Notification
from api.utils.servers import ServerAction
from api.utils import view_helper
import uuid


class RegisterView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        vk_id = request.GET.get('viewer_id')
        api_token = request.data.get('api_token')

        if not vk_id or not api_token:
            return HttpResponseBadRequest()

        token = str(uuid.uuid4())
        user, _ = User.objects.update_or_create(vk_id=vk_id, defaults={'token': token, 'api_token': api_token})
        user.create_or_update_projects()
        return Response(status=status.HTTP_201_CREATED, data={'token': token})


class ServersView(APIView):
    authentication_classes = (VkAuthentication,)
    renderer_classes = (JSONRenderer,)

    def get(self, request):
        res = view_helper.get_server_list(request.user)
        return Response(res)


class ServerDetailView(APIView):
    authentication_classes = (VkAuthentication,)
    renderer_classes = (JSONRenderer,)

    # parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data
        project_name = data.get('projectName')
        server_id = data.get('id')
        req = {
            'flavor_id': data.get('flavor_id'),
            'image_id': data.get('image_id'),
            'volume_id': data.get('volume_id'),
            'project': request.user.projects.filter(name=project_name).first()
        }
        if None in req.values():
            return HttpResponseBadRequest()
        details = view_helper.get_details(**req)
        details.update({'id': server_id})
        return Response(details)


class ServerHardReboot(APIView):
    authentication_classes = (VkAuthentication,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request, server_id):
        project_name = request.data.get('project_name')
        project = request.user.projects.filter(name=project_name).first()
        if not project:
            return HttpResponseBadRequest()
        sa = ServerAction(project, server_id)
        sa.hard_reboot()
        if not sa:
            return HttpResponseBadRequest()
        return Response()


class ServerSoftReboot(APIView):
    authentication_classes = (VkAuthentication,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request, server_id):
        project_name = request.data.get('project_name')
        project = request.user.projects.filter(name=project_name).first()
        if not project:
            return HttpResponseBadRequest()
        sa = ServerAction(project, server_id)
        sa.soft_reboot()
        if not sa:
            return HttpResponseBadRequest()
        return Response()


class ServerPause(APIView):
    authentication_classes = (VkAuthentication,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request, server_id):
        project_name = request.data.get('project_name')
        project = request.user.projects.filter(name=project_name).first()
        if not project:
            return HttpResponseBadRequest()
        sa = ServerAction(project, server_id)
        sa.pause()
        if not sa:
            return HttpResponseBadRequest()
        return Response()


class ServerUnpause(APIView):
    authentication_classes = (VkAuthentication,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request, server_id):
        project_name = request.data.get('project_name')
        project = request.user.projects.filter(name=project_name).first()
        if not project:
            return HttpResponseBadRequest()
        sa = ServerAction(project, server_id)
        sa.unpause()
        if not sa:
            return HttpResponseBadRequest()
        return Response()


class ServerStart(APIView):
    authentication_classes = (VkAuthentication,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request, server_id):
        project_name = request.data.get('project_name')
        project = request.user.projects.filter(name=project_name).first()
        if not project:
            return HttpResponseBadRequest()
        sa = ServerAction(project, server_id)
        sa.start()
        if not sa:
            return HttpResponseBadRequest()
        return Response()


class ServerStop(APIView):
    authentication_classes = (VkAuthentication,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request, server_id):
        project_name = request.data.get('project_name')
        project = request.user.projects.filter(name=project_name).first()
        if not project:
            return HttpResponseBadRequest()
        sa = ServerAction(project, server_id)
        sa.stop()
        if not sa:
            return HttpResponseBadRequest()
        return Response()


class NotificationView(APIView):
    authentication_classes = (VkAuthentication,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def post(self, request, server_id):
        project_name = request.data.get('project_name')
        req = {
            'project': request.user.projects.filter(name=project_name).first(),
            'server_id': server_id,
            'threshold': request.data.get('threshold'),
            'data_type': request.data.get('data_type')
        }
        if None in req.values():
            return Response(status=400)
        Notification.objects.create(**req)
        return Response()

    def get(self, request, server_id):
        notifications = request.user.projects.filter(notification__server_id=server_id)
        return Response(notifications)

    def put(self, request, server_id):
        n_id = request.data.get('notification_id')
        if not n_id:
            return Response(status=400)
        try:
            notification = Notification.objects.get()
        except Notification.DoesNotExist:
            return Response(status=404)
        to_update = request.data
        for k, v in to_update.items():
            setattr(notification, k, v)
        notification.save(update_fields=['threshold', 'is_running'])
        return Response()
