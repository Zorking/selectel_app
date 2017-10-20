import requests


def get_sid(username, password):
    login_url = 'https://my.selectel.ru/api/support/auth/login'
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }

    resp = requests.post(login_url, headers=headers, data={'login': username, 'password': password})
    if resp.status_code != 201:
        return
    return resp.cookies.get('sid')


def get_tickets(uid, sid):
    url = 'https://my.selectel.ru/api/internal/tickets'
    cookies = {'uid': str(uid), 'sid': sid}
    resp = requests.get(url, cookies=cookies)
    if resp.status_code != 200:
        return
    return resp.json()


def get_ticket(uid, sid, ticket_id):
    url = 'https://my.selectel.ru/api/internal/tickets/{}'.format(ticket_id)
    cookies = {'uid': str(uid), 'sid': sid}
    resp = requests.get(url, cookies=cookies)
    if resp.status_code != 200:
        return
    return resp.json()


def get_comments(uid, sid, ticket_id):
    url = 'https://my.selectel.ru/api/internal/tickets/{}/comments'.format(ticket_id)
    cookies = {'uid': str(uid), 'sid': sid}
    resp = requests.get(url, cookies=cookies)
    if resp.status_code != 200:
        return
    return resp.json()


def post_ticket(uid, sid, header, text):
    url = 'https://my.selectel.ru/api/internal/tickets'
    cookies = {'uid': str(uid), 'sid': sid}
    resp = requests.post(url, cookies=cookies, data={'header': header, 'text': text, 'tags[]': [23732, 23732]})
    if resp.status_code != 200:
        return
    return resp.json()
