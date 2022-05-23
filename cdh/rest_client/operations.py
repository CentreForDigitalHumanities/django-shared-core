from enum import Enum


class Operations(Enum):
    get = 1
    put = 2
    delete = 3
    get_over_post = 4  # When request params should be sent over POST instead of
    # GET. Mostly for logging in

