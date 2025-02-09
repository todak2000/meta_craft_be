# Generated by Django 4.1.1 on 2022-09-23 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_alter_client_avatar"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="address",
            field=models.TextField(
                blank=True, max_length=200, null=True, verbose_name="Address"
            ),
        ),
        migrations.AlterField(
            model_name="client",
            name="state",
            field=models.TextField(
                blank=True, max_length=200, null=True, verbose_name="State"
            ),
        ),
    ]
