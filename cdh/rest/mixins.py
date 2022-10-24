from importlib import import_module

from django.utils.module_loading import module_has_submodule

class ClientResourceSetupMixin:
    """This mixin can be used on an AppConfig, in order to populate the REST
    client registry with that app's Resource and Collection classes.

    By default it will try to import the resources module, but this can be
    changed by overriding the `resource_module` class variable.
    """

    resource_module = 'resources'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rest_module = None

    def ready(self):
        super().ready()
        from cdh.rest.client.logging import registry_logger as logger

        if module_has_submodule(self.module, self.resource_module):
            rest_module_name = '%s.%s' % (self.name, self.resource_module)
            self.rest_module = import_module(rest_module_name)
        else:
            logger.warning(
                "App '{}' has no '{}' module, but is configured to autoload "
                "resources/collections from it!".format(
                    self.name,
                    self.resource_module
                )
            )
