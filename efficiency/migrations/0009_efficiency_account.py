# Generated by Django 3.2.3 on 2021-10-14 20:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_customuser_active_nu_member'),
        ('efficiency', '0008_alter_efficiency_jobid'),
    ]

    operations = [
        migrations.AddField(
            model_name='efficiency',
            name='account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.account'),
        ),
    ]
