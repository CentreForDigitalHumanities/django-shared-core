from django.utils.datastructures import OrderedSet


class IndexedOrderedSet(OrderedSet):
    """
    A set which keeps the ordering of the inserted items. Additionally, it
    also support getting items by index.

    Django's OrderedSet doesn't support that, as set() doesn't support that.
    However, set() doesn't support it because it's _unordered_. Soooo, why
    _Ordered_Set doesn't support it is a bit unexplainable.
    """

    def __getitem__(self, item):
        items = list(self.dict.keys())
        return items[item]

    def __repr__(self):
        return repr(set(self.dict.keys()))
