from enum import IntEnum


class Text(IntEnum):
    pending_approval = -2
    error = -1
    started = 0
    in_work = 2
    complete = 100

    @classmethod
    def from_status(cls, status):
        try:
            return cls(status).name
        except ValueError:
            return "other"