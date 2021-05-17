from django.http import HttpResponse
from django.views import generic

from uil.vue.utils import get_vue_js, get_vue_css


class VueJSView(generic.View):

    def get(self, request, component, *args, **kwargs):
        from uil.vue.components import Vue

        c = Vue.get_component(component)

        return HttpResponse(get_vue_js(c), content_type='text/javascript')


class VueCSSView(generic.View):

    def get(self, request, component, *args, **kwargs):
        from uil.vue.components import Vue
        c = Vue.get_component(component)

        return HttpResponse(get_vue_css(c), content_type='text/css')

