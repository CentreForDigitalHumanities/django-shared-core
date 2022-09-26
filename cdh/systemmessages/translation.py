from modeltranslation.translator import register, TranslationOptions

from .models import SystemMessage


@register(SystemMessage)
class SystemMessageTranslationOptions(TranslationOptions):
    fields = ('message', )
