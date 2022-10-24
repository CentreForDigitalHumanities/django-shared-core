from typing import Iterable


class EnumerateTo:
    """
    Enumerates a given iterator up to a given n items. If the iterator can
    supply more than n items, the rest is ignored.

    If the iterator has less than n items, the remaining values will be
    filled in as None.
    """

    def __init__(self, iterable: Iterable, to_n: int, start: int=0):
        self.n = to_n
        self.iterable = iter(iterable)
        self.cursor = 0
        self.start = start

    def __iter__(self):
        return self

    def __next__(self) -> tuple:
        if self.cursor == self.n:
            raise StopIteration

        el = None
        n = self.cursor + self.start

        try:
            el = self.iterable.__next__()
        except StopIteration:
            pass

        self.cursor += 1

        return n, el


enumerate_to = EnumerateTo
