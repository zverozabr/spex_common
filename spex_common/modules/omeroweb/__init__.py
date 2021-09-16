from datetime import datetime, timedelta
from os import getenv
from ...models.OmeroSession import OmeroSession
from ..cache import cache_instance

__all__ = ['get', 'create', 'update_ttl', 'get_key']


def get_key(login):
    return f'omero_web_{login}'


def get_active_until():
    return datetime.now() + timedelta(hours=int(getenv('MEMCACHED_SESSION_ALIVE_H', 12)))


def _login_omero_web(login, password, server='1') -> OmeroSession or None:
    client = OmeroSession(active_until=get_active_until())

    response = client.get('/api/v0/token/')

    data = response.json()

    csrf_token = data['data']

    data = {
        'username': login,
        'password': password,
        'server': server
    }

    url = '/api/v0/login/'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrf_token
    }
    response = client.post(url, headers=headers, data=data)

    data = response.json()

    if response.status_code == 200 and data['success']:
        session = OmeroSession(
            response.cookies['sessionid'],
            csrf_token,
            data['eventContext'],
            get_active_until()
        )

        cache_instance().set(get_key(login), session)
    else:
        cache_instance().delete(get_key(login))

    return get(login)


def get(login) -> OmeroSession or None:
    session = cache_instance().get(get_key(login))

    if not (session and isinstance(session, OmeroSession)):
        return None

    timestamp = int(datetime.timestamp(datetime.now()) * 1000)

    url = f'/webclient/keepalive_ping/?_={timestamp}'
    response = session.get(url)

    if response.status_code == 200 and response.content.decode('utf8').lower() != 'connection failed':
        return session

    cache_instance().delete(get_key(login))

    return None


def create(login, password) -> OmeroSession or None:
    return _login_omero_web(login, password)


def update_ttl(login):
    session = get(login)

    if session is None:
        return

    session.update_active_until(get_active_until())

    cache_instance().set(get_key(login), session)
