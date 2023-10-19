# Generated by Django 4.0.8 on 2023-08-11 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dev_vue', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='exampledata',
            name='project_type',
            field=models.CharField(choices=[('S', 'Standard'), ('E', 'External'), ('TS', 'Top secret'), ('TK', 'Topsy Kretts')], default='S', max_length=2),
        ),
    ]