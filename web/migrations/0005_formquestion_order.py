# Generated by Django 4.1.4 on 2023-10-01 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_form_is_started_formquestion_is_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='formquestion',
            name='order',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]