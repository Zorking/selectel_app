from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api.auth import VkAuthentication
from api.models import User
from api.utils.servers import ServerAction
from api.utils.support import get_sid, get_tickets
from api.utils import view_helper


class RegisterView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        vk_id = request.GET.get('viewer_id')
        if not vk_id:
            return HttpResponseBadRequest()
        uid = request.data.get('uid')
        password = request.data.get('password')
        sid = get_sid(uid, password)
        if not sid:
            return HttpResponseBadRequest()
        User.objects.update_or_create(uid=uid, defaults={'sid': sid, 'vk_id': vk_id})
        return HttpResponse()


class TicketsView(APIView):
    authentication_classes = (VkAuthentication,)
    renderer_classes = (JSONRenderer,)
    parser_classes = (JSONParser,)

    def get(self, request):
        content = get_tickets(request.user.uid, request.user.sid)
        if not content:
            return HttpResponseBadRequest()
        return Response(content)

    def post(self, request):
        pass


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
