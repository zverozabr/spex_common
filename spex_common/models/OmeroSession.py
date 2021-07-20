from os import getenv
from urllib import parse
from requests import Session


class OmeroSession(Session):
    def __init__(self, session_id=None, token=None, context=None, active_until=None):
        super().__init__()
        self.__attrs__.extend([
            'omero_session_id',
            'omero_token',
            'omero_context',
            'active_until'
        ])
        self.omero_session_id = session_id
        self.omero_token = token
        self.omero_context = context
        self.active_until = active_until

        if session_id:
            self.cookies.setdefault('sessionid', session_id)

        if token:
            self.headers.setdefault('X-CSRFToken', token)

    def request(self, method: str, url: str, **kwargs):
        result = parse.urlparse(url)

        if not result.netloc or not result.scheme:
            url = parse.urljoin(getenv("OMERO_WEB"), url)

        return super(OmeroSession, self).request(
            method,
            url,
            **kwargs
        )
