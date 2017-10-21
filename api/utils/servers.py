import logging

import requests
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client

selectel_logger = logging.getLogger('selectel')


def authenticate_project(project_id, user_token):
    data = {'token': {'project_id': project_id}}
    resp = requests.post('https://api.selectel.ru/vpc/resell/v2/tokens', json=data,
                         headers={'X-token': str(user_token)})
    if resp.status_code != 200:
        selectel_logger.error(resp.url, resp.status_code, resp.content)
        return
    token = resp.json()
    if token:
        return token.get('token', {}).get('id')


def get_region(project_id, user_token):
    resp = requests.get('https://api.selectel.ru/vpc/resell/v2/projects/{}'.format(project_id),
                        headers={'X-token': str(user_token)})
    if resp.status_code != 200:
        selectel_logger.error(resp.url, resp.status_code, resp.content)
        return
    info = resp.json()
    if not info:
        return
    compute_cores = info.get('quotes', {}).get('compute_cores', [])
    for reg in compute_cores:
        if reg.get('used', 0) > 0:
            return reg.get('region')
    return 'ru-1'


def get_projects(user_token):
    resp = requests.get('https://api.selectel.ru/vpc/resell/v2/projects', headers={'X-token': user_token})
    if resp.status_code != 200:
        selectel_logger.error(resp.url, resp.status_code, resp.content)
        return []
    return resp.json().get('projects', [])


class ProjectConnector:
    def __init__(self, project):
        self.project = project
        self.nova = None
        self.auth()

    def auth(self, refresh=False):
        if refresh:
            self.project.update_auth()
        loader = loading.get_plugin_loader('token')
        auth = loader.load_from_options(auth_url='https://api.selvpc.ru/identity/v3',
                                        token=self.project.token,
                                        project_id=self.project.project_id)
        sess = session.Session(auth=auth)
        self.nova = client.Client(2.38, session=sess, region_name=self.project.region_name)

    def serialize_server(self, server):
        server_dict = {
            'id': server.id,
            'serverName': server.name,
            'tags': server.tags,
            'projectName': self.project.name,
            'region_name': self.project.region_name,
            'image_id': server.image.get('id'),
            'description': server.description,
            'flavor_id': server.flavor.get('id'),
            'status': server.status.lower()
        }
        subnet_ips = list(server.networks.values())
        ip = subnet_ips[0][0] if subnet_ips and subnet_ips[0] else None
        server_dict['ip'] = ip
        server_dict['volume_id'] = getattr(server, 'os-extended-volumes:volumes_attached')[0].get('id')
        return server_dict

    def get_all_servers(self, tags=None):
        res = []
        servers = self.nova.servers.list()
        for server in servers:
            res.append(self.serialize_server(server))
        return res

    def get_details(self, flavor_id, image_id, volume_id):
        res = {}
        res.update(self.get_flavor_info(flavor_id) or {})
        res.update(self.get_image_info(image_id) or {})
        res.update(self.get_volume_info(volume_id) or {})
        return res

    def get_volume_info(self, volume_id):
        resp = requests.get('https://api.selvpc.ru/volume/v3/{}/volumes/{}'.format(self.project.project_id, volume_id),
                            headers={'X-Auth-Token': self.project.token})
        if resp.status_code != 200:
            return
        volume = resp.json().get('volume', {})
        volume_type = 'fast' if 'fast' in volume.get('volume_type') else 'basic'
        return {'volume': {'size': volume.get('size') * 1024, 'type': volume_type}}

    def get_flavor_info(self, flavor_id):
        flavor = self.nova.flavors.find(id=flavor_id)
        if not flavor:
            return {}
        return {'ram': flavor.ram, 'cpus': flavor.vcpus}

    def get_image_info(self, image_id):
        resp = requests.get('https://api.selvpc.ru/compute/v2/images/{}'.format(image_id),
                            headers={'Content-Type': 'application/json',
                                     'X-Auth-Token': self.project.token,
                                     'X-OpenStack-Nova-Api-Version': '2.38'})
        if resp.status_code != 200:
            return
        return {'os': resp.json().get('image', {}).get('name')}
