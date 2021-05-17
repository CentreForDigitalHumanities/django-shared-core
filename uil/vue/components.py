import os
from typing import Dict, Optional, List

from django.conf import settings
from django.contrib.staticfiles import finders

try:
    from django.apps import apps
except ImportError:
    apps = False


class VueComponent:

    def __init__(
            self,
            name: str,
            location: str,
            subcomponents: Optional[List[str]] = None,
            depends: Optional[List[str]] = None,
    ):
        if subcomponents is None:
            subcomponents = ['subcomponents/*.vue']

        self.name = name
        self.subcomponents = subcomponents

        self.location = finders.find(location)
        self._dir = os.path.dirname(self.location)
        self.depends = depends

    def get_files(self) -> List[str]:
        locations = [self._dir + os.sep + sub for sub in self.subcomponents] + [self.location]

        if self.depends:
            for dependency in self.depends:
                component = Vue.get_component(dependency)
                # locations.extend(component.get_files())
                locations = component.get_files() + locations

        return locations


class _VueRegistry:
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if _VueRegistry.__instance is not None:
            _VueRegistry()
        return _VueRegistry.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if _VueRegistry.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            _VueRegistry.__instance = self

        self._components = {}
        self._loaded = False

    def _load(self):
        app_names = settings.INSTALLED_APPS
        if apps:
            app_names = [
                app_config.name
                for app_config in apps.get_app_configs()
            ]

        # loop through our INSTALLED_APPS
        for app in app_names:
            # skip any django apps
            if app.startswith("django."):
                continue

            vue_module = '%s.vue' % app
            try:
                __import__(vue_module)
            except ImportError:
                pass

    def add_component(self, component: VueComponent):
        self._components[component.name] = component

    def get_component(self, name: str) -> VueComponent:
        if not self._loaded:
            self._load()

        if name in self._components:
            return self._components[name]

        raise KeyError("{} is not a registered Vue component!".format(name))

    def get_components(self) -> Dict[str, VueComponent]:
        if not self._loaded:
            self._load()

        return self._components


Vue = _VueRegistry()
