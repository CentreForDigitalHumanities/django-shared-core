from django import template

from uil.core.file_loading import css, js

register = template.Library()


class FileNode(template.Node):
    def render(self, context):
        context.update({
            "uil_core_js_files": js,
            "uil_core_css_files": css,
        })

        return u""


@register.tag(name='load_file_vars')
def load_file_vars(parser, token):
    return FileNode()
