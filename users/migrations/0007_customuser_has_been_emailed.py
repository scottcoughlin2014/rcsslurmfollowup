# Generated by Django 3.2.3 on 2021-05-20 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_customuser_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='has_been_emailed',
            field=models.BooleanField(default=False),
        ),
    ]