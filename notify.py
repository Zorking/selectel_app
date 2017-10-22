#!/usr/bin/python3
import os
import django
import requests
import datetime
import vk
import io
import time
from django.conf import settings
from datetime import timedelta
from selectel_app import settings as app_settings
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(app_settings.BASE_DIR, 'db.sqlite3'),
        }
    },
    INSTALLED_APPS=('api',)
)

django.setup()

from api.models import *

API_TOKEN2 = 'c3b0a84b20be1ad10c1a20ca64741c1c5e919c22e38312bbf090df68bb69ed8015129cf1b7a7634db55f4'

ID = '49633824'

SELECTEL_LINK = 'https://api.selvpc.ru/metric/v1/resource/sel_instance/{0}' \
                '/metric/{2}/measures?granularity=300&start={1}'

SERVER_DETAIL_URL = 'https://api.selvpc.ru/compute/v2.1/servers/{}?detail'

METRIC_TYPES = {
    'cpu': {'name': 'cpu_util', 'label': 'CPU', 'quantity': '%'},
    'ram': {'name': 'memory.usage', 'label': 'RAM', 'quantity': 'MB'}
}

REPLY_LINK = 'https://api.vk.com/method/messages.send'


def create_image(data, metric_type):
    dates = [datetime.datetime.strptime(i[0].split('+')[0], '%Y-%m-%dT%X') for i in data]
    y_data = [d[2] for d in data]
    x_data = [i for i in range(len(y_data))]

    points = np.array([x_data, y_data]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, linewidths=4, color='green', antialiaseds=True)

    fig, a = plt.subplots(figsize=(12, 12))

    a.add_collection(lc)
    major_ticks = np.arange(0, len(dates), len(dates) / 5)

    a.tick_params(labelsize=16)
    a.set_xticks(major_ticks)
    a.set_xticklabels([d.strftime('%Y-%m-%d %H:%M') for i, d in enumerate(dates) if i % 5 == 0], rotation='horizontal',
                      fontsize=14)

    plt.ylim(min(y_data) - (min(y_data) * 0.1), max(y_data) + (max(y_data) * 0.1))
    plt.xlim(min(x_data), max(x_data))

    plt.xlabel('Время', fontsize=18)
    plt.ylabel('Загрузка ({})'.format(metric_type['quantity']), fontsize=18)
    plt.title('Отчет по {}'.format(metric_type['label']), fontdict={'fontsize': 20})
    plt.grid(True)

    buf = io.BytesIO()
    plt.savefig(buf)
    buf.seek(0, 0)
    return buf


def check_notifications(notify):
    print('Checking notifications')

    time_range = datetime.datetime.utcnow() - timedelta(minutes=120)
    metric_url = SELECTEL_LINK.format(notify.server_id, time_range, METRIC_TYPES.get(notify.data_type)['name'])

    headers = {
        'X-Auth-Token': notify.project.token
    }

    response = requests.get(metric_url, headers=headers)

    print(response.status_code)

    if response.status_code == 200:
        data = response.json()
        current_data = data[-1]
        data_time = current_data[0]
        current_threshold = current_data[2]

        data_time = datetime.datetime.strptime(data_time.split('+')[0], '%Y-%m-%dT%X')

        if notify.last_call:
            plus_date = notify.last_call + datetime.timedelta(minutes=1)
        else:
            plus_date = data_time

        if current_threshold > notify.threshold and data_time >= plus_date:
            metric_image = create_image(data, METRIC_TYPES.get(notify.data_type))
            user_vk_id = notify.project.user.vk_id
            session = vk.Session(access_token=API_TOKEN2)
            vkapi = vk.API(session)

            upload_url = vkapi.photos.getMessagesUploadServer(peer_id=user_vk_id)

            ur = requests.post(upload_url['upload_url'],
                               files={'photo': ('metric.png', metric_image.getvalue())}).json()
            result = vkapi.photos.saveMessagesPhoto(photo=ur['photo'], server=ur['server'], hash=ur['hash'])

            res = requests.get(
                SERVER_DETAIL_URL.format(notify.server_id),
                headers=headers)

            message = '''❗️❗️❗️ \nДостигнут лимит {}\n❗️❗️❗\nСервер: {}\nЛимит: {}{}\nАктуальное значение: {}\n
                      '''.format(METRIC_TYPES.get(notify.data_type)['label'],
                                 res.json()['server']['name'],
                                 notify.threshold,
                                 METRIC_TYPES.get(notify.data_type)['quantity'],
                                 current_threshold)

            vkapi.messages.send(user_id=user_vk_id, message=message, attachment=result[0]['id'])

            notify.last_call = data_time
            notify.save()

            print('Sent')


while True:
    notifies = Notification.objects.filter(is_running=True)

    for notify in notifies:
        try:
            check_notifications(notify)
        except Exception as e:
            print(e)
            pass

    time.sleep(300)
