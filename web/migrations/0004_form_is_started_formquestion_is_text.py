# Generated by Django 4.1.4 on 2023-10-01 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_forminfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='is_started',
            field=models.BooleanField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='formquestion',
            name='is_text',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
