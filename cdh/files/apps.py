from django.apps import AppConfig

from cdh.core.file_loading import add_css_file, add_js_file


class FilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cdh.files'

    def ready(self):
        import cdh.files.checks  # noQA, the import has side effects, linter!
        import cdh.files.signals # noQA, same story

        add_js_file('cdh.files/widgets.js')
        add_css_file('cdh.files/widgets.css')
