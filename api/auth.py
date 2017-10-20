from api.models import User
from rest_framework import authentication
from rest_framework import exceptions


class VkAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        vk_id = request.GET.get('viewer_id')
        if not vk_id:
            return None

        try:
            user = User.objects.get(vk_id=vk_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')
        return user, None