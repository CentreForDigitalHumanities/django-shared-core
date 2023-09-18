from django import forms

from cdh.core.forms import BootstrapSelect, TemplatedForm, TemplatedModelForm
from cdh.integration_platform.digital_identity_api.forms.widgets import \
    SingleUserWidget
from .models import Record

YES_NO = (
    (True, 'Yes'),
    (False, 'No'),
)


class DIATest(TemplatedForm):

    identity = forms.CharField()

    identity_type = forms.ChoiceField(
        widget=BootstrapSelect,
        choices=(
            ('solisid', "Solis-ID"),
            ('email', "E-mail"),
            ('student_number', "Student number"),
            ('employee_number', "Employee number"),
            ('employee_cp_number', "Employee cp number"),
        )
    )

    person = forms.BooleanField(
        widget=BootstrapSelect(choices=YES_NO),
        required=False,
    )
    role = forms.BooleanField(
        widget=BootstrapSelect(choices=YES_NO),
        required=False,
    )
    email = forms.BooleanField(
        widget=BootstrapSelect(choices=YES_NO),
        required=False,
    )
    external_id = forms.BooleanField(
        widget=BootstrapSelect(choices=YES_NO),
        required=False,
    )


class DIAUsersTest(TemplatedModelForm):
    class Meta:
        model = Record
        fields = '__all__'
        widgets = {
            'main_user': SingleUserWidget
        }
