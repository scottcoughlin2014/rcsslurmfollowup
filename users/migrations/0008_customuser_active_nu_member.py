# Generated by Django 3.2.3 on 2021-06-29 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_customuser_has_been_emailed'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='active_nu_member',
            field=models.BooleanField(default=True),
        ),
    ]
