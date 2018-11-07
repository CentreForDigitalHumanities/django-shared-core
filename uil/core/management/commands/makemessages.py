from django.core.management.commands.makemessages import Command as C, BuildFile as BF, prepare_js_for_gettext
from django.conf import settings
import re


def templatize(src, **kwargs):
    """
    This function overrides part of the original templetize function used by BuildFile below, by sligtly modifying
    the inline_re variable to include the transformat tag.
    :param src:
    :param kwargs:
    :return:
    """
    print("patching patching patching")
    import django.utils.translation.template as template

    template.inline_re = re.compile(
        # Match the trans 'some text' part
        r"""^\s*trans(?:format)?\s+((?:"[^"]*?")|(?:'[^']*?'))"""
        # Match and ignore optional filters
        r"""(?:\s*\|\s*[^\s:]+(?::(?:[^\s'":]+|(?:"[^"]*?")|(?:'[^']*?')))?)*"""
        # Match the optional context part
        r"""(\s+.*context\s+((?:"[^"]*?")|(?:'[^']*?')))?\s*"""
    )

    return template.templatize(src, **kwargs)


class BuildFile(BF):

    def preprocess(self):
        """
        Preprocess (if necessary) a translatable file before passing it to
        xgettext GNU gettext utility.
        """
        if not self.is_templatized:
            return

        encoding = settings.FILE_CHARSET if self.command.settings_available else 'utf-8'
        with open(self.path, 'r', encoding=encoding) as fp:
            src_data = fp.read()

        if self.domain == 'djangojs':
            content = prepare_js_for_gettext(src_data)
        elif self.domain == 'django':
            content = templatize(src_data, origin=self.path[2:])

        with open(self.work_path, 'w', encoding='utf-8') as fp:
            fp.write(content)


class Command(C):
    build_file_class = BuildFile
