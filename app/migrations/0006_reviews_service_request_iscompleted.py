# Generated by Django 4.1.1 on 2022-09-23 08:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0005_service_request"),
    ]

    operations = [
        migrations.CreateModel(
            name="Reviews",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "service_id",
                    models.TextField(max_length=200, verbose_name="Service ID"),
                ),
                (
                    "client_id",
                    models.TextField(max_length=999, verbose_name="Client ID"),
                ),
                ("sp_id", models.TextField(max_length=999, verbose_name="Provider ID")),
                (
                    "comment",
                    models.IntegerField(
                        blank=True, verbose_name="Comment/Review from Client"
                    ),
                ),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                "db_table": "Service_Reviews_Table",
            },
        ),
        migrations.AddField(
            model_name="service_request",
            name="isCompleted",
            field=models.BooleanField(
                default=False, verbose_name="Client Confirm Job done"
            ),
        ),
    ]