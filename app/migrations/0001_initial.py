# Generated by Django 4.1.1 on 2022-09-15 16:54

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Client",
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
                ("_id", models.CharField(max_length=50, unique=True)),
                (
                    "firstname",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="Firstname"
                    ),
                ),
                (
                    "lastname",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="Lastname"
                    ),
                ),
                (
                    "email",
                    models.EmailField(max_length=90, unique=True, verbose_name="Email"),
                ),
                (
                    "phone",
                    models.CharField(
                        max_length=15,
                        null=True,
                        unique=True,
                        verbose_name="Telephone number",
                    ),
                ),
                ("password", models.TextField(max_length=200, verbose_name="Password")),
                (
                    "address",
                    models.TextField(max_length=200, null=True, verbose_name="Address"),
                ),
                (
                    "state",
                    models.TextField(max_length=200, null=True, verbose_name="State"),
                ),
                (
                    "avatar",
                    models.CharField(
                        max_length=999, null=True, verbose_name="Client Picture/Avatar"
                    ),
                ),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                "db_table": "Clients_table",
            },
        ),
        migrations.CreateModel(
            name="Gallery",
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
                ("sp_id", models.TextField(max_length=20, verbose_name="SP ID")),
                (
                    "url",
                    models.TextField(max_length=500, verbose_name="Gallery Item URL"),
                ),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                "db_table": "Gallaries_Table",
            },
        ),
        migrations.CreateModel(
            name="Otp",
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
                    "user_id",
                    models.TextField(max_length=20, verbose_name="Client/SP ID"),
                ),
                ("otp_code", models.TextField(max_length=20, verbose_name="OTP CODE")),
                ("validated", models.BooleanField(default=False)),
                (
                    "password_reset_code",
                    models.TextField(
                        default="", max_length=20, verbose_name="Reset Code"
                    ),
                ),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                "db_table": "OTP_Code_Table",
            },
        ),
        migrations.CreateModel(
            name="Review",
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
                ("sp_id", models.TextField(max_length=20, verbose_name="SP ID")),
                (
                    "client_id",
                    models.TextField(max_length=20, verbose_name="Client ID"),
                ),
                (
                    "comment",
                    models.TextField(max_length=999, verbose_name="Review Comment"),
                ),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                "db_table": "Reviews_Table",
            },
        ),
        migrations.CreateModel(
            name="Service",
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
                ("service_name", models.TextField(max_length=20, verbose_name="SP ID")),
                (
                    "type",
                    models.TextField(
                        max_length=999, verbose_name="Type of Service (Norma/Special"
                    ),
                ),
                (
                    "service_avatar",
                    models.TextField(max_length=500, verbose_name="Service Avatar"),
                ),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                "db_table": "Services_Table",
            },
        ),
        migrations.CreateModel(
            name="Sub_Service",
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
                    "main_service_id",
                    models.TextField(max_length=20, verbose_name="Main Service ID"),
                ),
                (
                    "name",
                    models.TextField(max_length=500, verbose_name="Sub_Service name"),
                ),
                (
                    "price",
                    models.TextField(max_length=999, verbose_name="Prove of Service"),
                ),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                "db_table": "Sub_Services_Table",
            },
        ),
        migrations.CreateModel(
            name="Service_Provider",
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
                ("_id", models.CharField(max_length=50, unique=True)),
                (
                    "firstname",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="Firstname"
                    ),
                ),
                (
                    "lastname",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="Lastname"
                    ),
                ),
                (
                    "email",
                    models.EmailField(max_length=90, unique=True, verbose_name="Email"),
                ),
                (
                    "phone",
                    models.CharField(
                        max_length=15,
                        null=True,
                        unique=True,
                        verbose_name="Telephone number",
                    ),
                ),
                ("password", models.TextField(max_length=200, verbose_name="Password")),
                (
                    "address",
                    models.TextField(max_length=200, null=True, verbose_name="Address"),
                ),
                (
                    "state",
                    models.TextField(max_length=200, null=True, verbose_name="State"),
                ),
                (
                    "avatar",
                    models.CharField(
                        max_length=999, null=True, verbose_name="SP Picture/Avatar"
                    ),
                ),
                (
                    "ratings",
                    models.FloatField(
                        default=1.0, max_length=200, verbose_name="Job Ratings"
                    ),
                ),
                (
                    "pitch",
                    models.CharField(max_length=999, null=True, verbose_name="Pitch"),
                ),
                ("date_added", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "gallery",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="app.gallery"
                    ),
                ),
                (
                    "reviews",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="app.review"
                    ),
                ),
                (
                    "services_rendered",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="app.service"
                    ),
                ),
            ],
            options={
                "db_table": "Service_Providers_table",
            },
        ),
        migrations.AddField(
            model_name="service",
            name="sub_service",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="app.sub_service"
            ),
        ),
    ]
