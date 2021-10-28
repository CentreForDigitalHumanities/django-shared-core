from django.apps import AppConfig

from uil.core.file_loading import add_css_file, add_js_file


class FilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'uil.files'

    def ready(self):
        import uil.files.checks  # noQA, the import has side effects, linter!
        import uil.files.signals # noQA, same story

        add_js_file('uil.files/widgets.js')
        add_css_file('uil.files/widgets.css')
