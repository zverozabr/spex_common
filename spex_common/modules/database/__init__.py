from os import getenv
from .model import ArangoDB

__instance: ArangoDB or None = None


def db_instance() -> ArangoDB:
    global __instance
    if __instance is None:
        __instance = ArangoDB(
            getenv('ARANGODB_DATABASE_URL'),
            getenv('ARANGODB_DATABASE_NAME'),
            getenv('ARANGODB_USERNAME'),
            getenv('ARANGODB_PASSWORD')
        )
        __instance.initialize()

    return __instance
