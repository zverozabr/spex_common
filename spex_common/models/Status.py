from enum import IntEnum


class Text(IntEnum):
    failed = -3
    pending_approval = -2
    error = -1
    started = 0
    in_work = 2
    complete = 100

    @classmethod
    def from_status(cls, status) -> str:
        try:
            return cls(status).name
        except ValueError:
            return "other"

    @classmethod
    def from_str(cls, status) -> int:
        try:
            return cls(status).value
        except ValueError:
            return -3


class PipelineText(IntEnum):
    stopped = -3
    pending_approval = -2
    started = 0
    complete = 100

    @classmethod
    def from_status(cls, status) -> str:
        try:
            return cls(status).name
        except ValueError:
            return "in progress"

    @classmethod
    def from_str(cls, status) -> int:
        try:
            return cls(status).value
        except ValueError:
            return 1