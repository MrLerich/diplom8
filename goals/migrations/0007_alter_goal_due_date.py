# Generated by Django 4.1.5 on 2023-01-18 19:05

from django.db import (
    migrations,
    models
)


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0006_alter_goalcomment_options_alter_goalcomment_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='due_date',
            field=models.DateField(null=True, verbose_name='Дата выполнения'),
        ),
    ]
