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


def get_projects(user_token):
    resp = requests.get('https://api.selectel.ru/vpc/resell/v2/projects', headers={'X-token': user_token})
    if resp.status_code != 200:
        selectel_logger.error(resp.url, resp.status_code, resp.content)
        return []
    return resp.json().get('projects', [])


class ProjectConnector:
    def __init__(self, project):
        self.project = project
        loader = loading.get_plugin_loader('token')
        auth = loader.load_from_options(auth_url='https://api.selvpc.ru/identity/v3',
                                        token=project.token,
                                        project_id=project.project_id)
        sess = session.Session(auth=auth)
        self.nova = client.Client(2.38, session=sess, region_name='ru-1')

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
        return resp.json().get('image', {}).get('name')

    def serialize_server(self, server):
        server_dict = {
            'id': server.id,
            'serverName': server.name,
            'tags': server.tags,
            'projectName': self.project.name,
            'os': self.get_image_info(server.image.get('id')),
            'description': server.description,
        }
        server_dict.update(self.get_flavor_info(server.flavor.get('id')))
        subnet_ips = list(server.networks.values())
        ip = subnet_ips[0][0] if subnet_ips and subnet_ips[0] else None
        server_dict['ip'] = ip
        return server_dict

    def get_all_servers(self, tags=None):
        from pprint import pprint
        servers = self.nova.servers.list()
        pprint(servers[0].__dir__())
        for server in servers:
            pprint(self.serialize_server(server))

            # print(nova.flavors.list())

# servers = nova.servers.list()
# print(servers[0])
# print(dir(servers[0]))
# print(servers[0].networks)
# print(servers[0].flavor)
# print(servers[0].status)
# print(servers[0].set_tags(['asd', 'tes8t', 'jjj']))
# print(servers[0].tag_list())
# print(servers[0].tags)
