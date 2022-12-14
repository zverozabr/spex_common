import traceback
from datetime import datetime, timedelta
from os import getenv
from omero.gateway import BlitzGateway
from ...models.OmeroBlitzSession import OmeroBlitzSession
from ..redis import redis_instance

__all__ = ['get', 'create', 'update_ttl', 'get_key']


def get_key(login):
    return f'omero_blitz_{login}'


def get_active_until():
    return datetime.now() + timedelta(hours=int(getenv('REDIS_SESSION_ALIVE_H', 12)))


def _login_omero_blitz(login, password) -> OmeroBlitzSession or None:
    active_until = get_active_until()

    host = getenv('OMERO_HOST')

    client = BlitzGateway(login, password, host=host, secure=True)

    if client.connect():
        # client.c.stopKeepAlive()
        client.c.enableKeepAlive(60)
        session_id = client.getEventContext().sessionUuid

        session = OmeroBlitzSession(session_id, active_until, host)
        redis_instance().set(get_key(login), session.serialize())
    else:
        redis_instance().delete(get_key(login))

    return get(login)


def get(login, keep_alive=True) -> OmeroBlitzSession or None:
    session = redis_instance().get(get_key(login))
    session = OmeroBlitzSession.deserialize(session)

    if not isinstance(session, OmeroBlitzSession):
        return None

    try:
        if session.connect():
            user = session.get_gateway().getUser()

            if user is not None:
                if not keep_alive:
                    session.get_gateway().c.stopKeepAlive()

                return session

        redis_instance().delete(get_key(login))
    except Exception:
        traceback.print_exc()

    return None


def create(login, password) -> OmeroBlitzSession or None:
    return _login_omero_blitz(login, password)


def update_ttl(login):
    pass
