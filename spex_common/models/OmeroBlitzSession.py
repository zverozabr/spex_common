from os import getenv
from omero.gateway import BlitzGateway


class OmeroBlitzSession:
    _gateway: BlitzGateway or None = None

    def __init__(self, session_id, active_until, host):
        self.session_id = session_id
        self.host = host
        self.active_until = active_until

    def connect(self) -> bool:
        if not self.host:
            raise Exception("OmeroBlitzSession: host is not set")

        if not self.session_id:
            raise Exception("OmeroBlitzSession: session_id is not set")

        self._gateway = BlitzGateway(self.session_id, self.session_id, host=self.host, secure=True)
        if not self._gateway.connect(self.session_id):
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
                .getReferenceCount(self.session_id)
            if ref_count < 2:
                return

        if hard:
            self._gateway.c.stopKeepAlive()
        self._gateway.close(hard)
