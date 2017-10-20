import json

from django.http import HttpResponseBadRequest


def register(request):
    if request.method == 'POST':
        vk_id = request.GET.get('viewer_id')
        if not vk_id:
            return HttpResponseBadRequest()
        uid = request.POST.get('uid')
        password = request.POST.get('password')
    elif request.method == 'GET':
        pass
