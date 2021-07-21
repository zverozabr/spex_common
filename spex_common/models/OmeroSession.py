from os import getenv
from urllib import parse
from requests import Session
import warnings


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

        omero_web_url = getenv("OMERO_WEB")

        if not omero_web_url:
            warnings.warn('OMERO_WEB is not defined in env')

        if omero_web_url and not (result.netloc and result.scheme):
            url = parse.urljoin(omero_web_url, url)

        return super(OmeroSession, self).request(
            method,
            url,
            **kwargs
        )
