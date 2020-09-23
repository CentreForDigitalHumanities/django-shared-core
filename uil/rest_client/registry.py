

class _RestRegistry:

    def __init__(self):
        self.resource_registry = {}
        self.collection_registry = {}

    def register_resource(self, app_label: str, resource: object) -> None:
        resource_name = resource.__name__

        if app_label not in self.resource_registry:
            self.resource_registry[app_label] = {}

        if resource in self.resource_registry[app_label]:
            raise RuntimeError(
                "Conflicting '{}' resources in app '{}'".format(
                    resource_name,
                    app_label
                )
            )

        self.resource_registry[app_label][resource_name] = resource

    def register_collection(self, app_label: str, collection: object) -> None:
        collection_name = collection.__name__

        if app_label not in self.collection_registry:
            self.collection_registry[app_label] = {}

        if collection in self.collection_registry[app_label]:
            raise RuntimeError(
                "Conflicting '{}' resources in app '{}'".format(
                    collection_name,
                    app_label
                )
            )

        self.collection_registry[app_label][collection_name] = collection

    def get_collection(self, app_label: str, collection_name: str=None):
        if collection_name is None:
            app_label, collection_name = app_label.split('.')

        if app_label not in self.collection_registry:
            raise LookupError

        if collection_name not in self.collection_registry[app_label]:
            raise LookupError

        return self.collection_registry[app_label][collection_name]

    def get_resource(self, app_label: str, resource_name: str = None):
        if resource_name is None:
            app_label, resource_name = app_label.split('.')

        if app_label not in self.resource_registry:
            raise LookupError

        if resource_name not in self.resource_registry[app_label]:
            raise LookupError

        return self.resource_registry[app_label][resource_name]


registry = _RestRegistry()
