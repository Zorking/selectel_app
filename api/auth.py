from api.models import User
from rest_framework import authentication
from rest_framework import exceptions


class VkAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        vk_id = request.GET.get('viewer_id')
        token = request.META['HTTP_AUTHORIZATION']

        if not vk_id or not token:
            raise exceptions.AuthenticationFailed

        try:
            user = User.objects.get(vk_id=vk_id, token=token)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')
        return user, None
