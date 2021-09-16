from os import getenv
from omero.gateway import BlitzGateway


class OmeroBlitzSession:
    _gateway: BlitzGateway or None = None

    __attrs__ = ['_session_id', '_host', 'active_until']

    def __init__(self, session_id, active_until, host=getenv("OMERO_HOST")):
        self._session_id = session_id
        self._host = host
        self.active_until = active_until

    def connect(self) -> bool:
        if not self._host:
            raise Exception("OmeroBlitzSession: host is not set")

        if not self._session_id:
            raise Exception("OmeroBlitzSession: session_id is not set")

        self._gateway = BlitzGateway(self._session_id, self._session_id, host=self._host, secure=True)
        if not self._gateway.connect(self._session_id):
            raise Exception("OmeroBlitzSession: can't connect")

        self._gateway.c.enableKeepAlive(60)

        return True

    def get_gateway(self):
        return self._gateway

    def close(self, hard=False):
        if self._gateway is None:
            return

        if not hard:
            ref_count = self._gateway.c.sf\
                .getSessionService()\
                .getReferenceCount(self._session_id)
            if ref_count < 2:
                return

        self._gateway.close(hard)
