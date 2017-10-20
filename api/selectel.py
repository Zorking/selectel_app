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

