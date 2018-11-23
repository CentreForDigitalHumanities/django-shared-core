from django.template import Library, Node, TemplateSyntaxError
from django.utils.translation import get_language
from django.utils.safestring import mark_safe
from django.templatetags.static import static

register = Library()


class TranslateInfoNode(Node):

    def render(self, context):
        link = 'uil.core/js/datatables/lang/english.json'
        if get_language() == 'nl':
            link = 'uil.core/js/datatables/lang/dutch.json'

        link = '{ &quot;url&quot;: &quot;%s&quot; }' % static(link).replace('/', '\/')

        return mark_safe(link)


@register.tag('datatables_lang')
def do_add_datatables_lang(parser, token):
    """
    This tag outputs the correct value for the data-language attribute
    """
    bits = token.split_contents()
    if len(bits) != 1:
        raise TemplateSyntaxError("'%s' takes no arguments" % bits[0])

    return TranslateInfoNode()
