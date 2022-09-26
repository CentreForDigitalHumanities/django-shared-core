from django.db.models import TextField
from django.contrib import admin

from cdh.core.forms import TinyMCEWidget

from .models import SystemMessage


class SystemMessageAdmin(admin.ModelAdmin):
    class Media:
        js = (
            'cdh.core/js/jquery-3.6.1.min.js',
            'cdh.core/js/tinymce/tinymce.min.js',
            'cdh.core/js/tinymce/tinymce-jquery.min.js',
            'cdh.core/js/tinymce/shim.js',
        )
    formfield_overrides = {
        TextField: {"widget": TinyMCEWidget},
    }


admin.site.register(SystemMessage, SystemMessageAdmin)
