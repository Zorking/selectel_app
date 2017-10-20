from django.http import HttpResponseBadRequest, HttpResponse
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from api.auth import VkAuthentication
from api.models import User
from api.selectel import get_sid, get_tickets


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
