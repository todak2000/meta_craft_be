# Generated by Django 4.1.1 on 2022-09-23 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_remove_service_provider_gallery_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="avatar",
            field=models.CharField(
                blank=True,
                max_length=999,
                null=True,
                verbose_name="Client Picture/Avatar",
            ),
        ),
    ]
