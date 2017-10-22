from django.http import Http404
from keystoneauth1.exceptions import NotFound as keystone_err
from novaclient.exceptions import NotFound as nova_err

from .servers import ProjectConnector


def get_server_list(user):
    res = []
    for project in user.projects.all():
        conn = ProjectConnector(project)
        try:
            servers = conn.get_all_servers()
        except (keystone_err, nova_err):
            conn.auth(refresh=True)
            try:
                servers = conn.get_all_servers()
            except (keystone_err, nova_err):
                servers = []
        res.extend(servers)
    return res


def get_details(project, flavor_id, image_id, volume_id):
    conn = ProjectConnector(project)
    try:
        return conn.get_details(flavor_id, image_id, volume_id)
    except (keystone_err, nova_err):
        conn.auth(refresh=True)
        try:
            return conn.get_details(flavor_id, image_id, volume_id)
        except (keystone_err, nova_err):
            raise Http404()

def registration(vk_id, api_token):
    pass
