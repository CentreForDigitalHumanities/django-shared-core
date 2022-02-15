from django import template

from cdh.core.file_loading import css, js

register = template.Library()


class FileNode(template.Node):
    def render(self, context):
        context.update({
            "cdh_core_js_files": js,
            "cdh_core_css_files": css,
        })

        return u""


@register.tag(name='load_file_vars')
def load_file_vars(parser, token):
    return FileNode()
