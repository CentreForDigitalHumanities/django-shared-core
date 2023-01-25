from typing import List, Tuple

import cdh.vue.vbuild as vbuild

from .components import VueComponent


def _render(component: VueComponent) -> vbuild.VBuild:
    return vbuild.render(component)


def get_vue_js(component: VueComponent) -> str:
    return _render(component).script


def get_vue_css(component: VueComponent) -> str:
    return _render(component).style


def get_vue_template_ids(component: VueComponent) -> List[str]:
    # TODO: optimize this so it doesn't require a render
    templates = _render(component)._html # NoQA

    return [tid for (tid, _) in templates]


def get_vue_templates(component: VueComponent) -> Tuple[str, str]:
    return  _render(component)._html


def get_vue_template(component: VueComponent, template: str) -> str:
    templates = _render(component)._html # NoQA

    for tid, tmplt in templates:
        if tid == template:
            return tmplt

    return ""
