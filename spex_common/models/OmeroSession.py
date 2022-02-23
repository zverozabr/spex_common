from os import getenv
from urllib import parse
from requests import Session
from .Serializable import Serializable
import warnings


class OmeroSession(Session, Serializable):
    def __init__(self, session_id=None, token=None, context=None, active_until=None):
        super().__init__()
        self.__attrs__.extend([
            '__attrs__',
            'omero_session_id',
            'omero_token',
            'omero_context',
            'omero_web_url',
            'active_until'
        ])
        self.omero_session_id = session_id
        self.omero_token = token
        self.omero_context = context
        self.omero_web_url = getenv("OMERO_WEB")
        self.active_until = active_until

        if not self.omero_web_url:
            warnings.warn('OMERO_WEB is not defined in env')

        self.verify = False

        if session_id:
            self.cookies.setdefault('sessionid', session_id)

        if token:
            self.headers.setdefault('X-CSRFToken', token)

    def get_host(self):
        return self.omero_web_url

    def request(self, method: str, url: str, **kwargs):
        result = parse.urlparse(url)

        if not self.omero_web_url:
            warnings.warn('OMERO_WEB is not defined in env')

        if self.omero_web_url and not (result.netloc and result.scheme):
            url = parse.urljoin(self.omero_web_url, url)

        return super(OmeroSession, self).request(
            method,
            url,
            **kwargs
        )

    def update_active_until(self, active_until):
        self.active_until = active_until
