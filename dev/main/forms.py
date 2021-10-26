from django import forms
from uil.core import fields as core_fields


class FormStylesForm(forms.Form):
    text = forms.CharField()

    textarea = forms.ChoiceField(
        widget=forms.Textarea
    )

    django_date = forms.DateField(
        help_text="Using django's version of the field"
    )

    django_time = forms.TimeField(
        help_text="Using django's version of the field"
    )

    django_datetime = forms.DateTimeField(
        help_text="Using django's version of the field"
    )

    django_split_datetime = forms.SplitDateTimeField(
        help_text="Using django's version of the field"
    )

    core_date = core_fields.DateField(
        help_text="Using core's version of the field"
    )

    core_time = core_fields.TimeField(
        help_text="Using core's version of the field"
    )

    core_datetime = core_fields.DateTimeField(
        help_text="Using core's version of the field"
    )

    core_split_datetime = core_fields.SplitDateTimeField(
        help_text="Using django's version of the field"
    )

    checkbox = forms.BooleanField()

    choice = forms.ChoiceField(choices=[
        (1, "Train"),
        (2, "Bus"),
        (3, "Aeroplane"),
        (4, "Bike"),
        (5, "Feet"),
        (6, "Magical Unicorn"),
        (6, "Broom"),
        (6, "Thestrals"),
    ])

    typed_choice = forms.TypedChoiceField(choices=[
        (1, "Train"),
        (2, "Bus"),
        (3, "Aeroplane"),
        (4, "Bike"),
        (5, "Feet"),
        (6, "Magical Unicorn"),
        (6, "Broom"),
        (6, "Thestrals"),
    ])

    radio = forms.TypedChoiceField(
        choices=[
            (1, "Train"),
            (2, "Bus"),
            (3, "Aeroplane"),
            (4, "Bike"),
            (5, "Feet"),
            (6, "Magical Unicorn"),
            (6, "Broom"),
            (6, "Thestrals"),
        ],
        widget=forms.RadioSelect
    )

    integer = forms.IntegerField()

    float = forms.FloatField(help_text="Floating away")

    decimal = forms.DecimalField()

    email = forms.EmailField()

    telephone = core_fields.TelephoneField()

    color = core_fields.ColorField()

    image = forms.ImageField()

    file = forms.FileField(help_text="Not an UiL.files field ;)")

    IP = forms.GenericIPAddressField()

    url = forms.URLField()

    UUID = forms.UUIDField()

    password = core_fields.PasswordField()


class JqueryUIFormStylesForm(forms.Form):
    date = forms.DateField()

