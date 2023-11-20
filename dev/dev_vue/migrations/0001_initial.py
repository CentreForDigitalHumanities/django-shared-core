# Generated by Django 4.0.8 on 2023-08-07 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExampleData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.TextField()),
                ('project_owner', models.TextField()),
                ('reference_number', models.TextField()),
                ('status', models.CharField(choices=[('O', 'Open'), ('R', 'In review'), ('C', 'Concluded')], default='O', max_length=2)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
