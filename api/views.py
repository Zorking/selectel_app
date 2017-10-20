import json

from django.http import HttpResponseBadRequest


def register(request):
    vk_id = request.GET.get('viewer_id')
    if not vk_id:
        return HttpResponseBadRequest()
