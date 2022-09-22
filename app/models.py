from django.db import models
from django.utils import timezone
from django.db.models.deletion import CASCADE
from django.contrib.postgres.fields import ArrayField
import json
from .CustomCode import distance

# Create your models here.
def format_data(data):
    formated_data = [item.long() for item in data]
    return formated_data


def format_sp_data(data, long, lat):
    formated_data = [item.longer(long, lat) for item in data]
    return formated_data


def get_list_default():
    return list(dict(["Hair Stylist", "Barber"]).keys())


class Otp(models.Model):
    class Meta:
        db_table = "OTP_Code_Table"

    user_id = models.TextField(verbose_name="Client/SP ID", max_length=20)
    otp_code = models.TextField(max_length=20, verbose_name="OTP CODE")
    validated = models.BooleanField(default=False)
    password_reset_code = models.TextField(
        max_length=20, verbose_name="Reset Code", default=""
    )
    date_added = models.DateTimeField(default=timezone.now)

    def long(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "otp_code": self.otp_code,
            "validated": self.validated,
            "password_reset_code": self.password_reset_code,
        }

    def __str__(self):
        return json.dumps(self.long())


class Client(models.Model):
    class Meta:
        db_table = "Clients_table"

    _id = models.CharField(max_length=50, unique=True)
    firstname = models.CharField(max_length=30, verbose_name="Firstname", blank=True)
    lastname = models.CharField(max_length=30, verbose_name="Lastname", blank=True)
    email = models.EmailField(max_length=90, unique=True, verbose_name="Email")
    phone = models.CharField(
        max_length=15, unique=True, null=True, verbose_name="Telephone number"
    )
    password = models.TextField(max_length=200, verbose_name="Password")
    address = models.TextField(max_length=200, verbose_name="Address", null=True)
    state = models.TextField(max_length=200, verbose_name="State", null=True)
    avatar = models.CharField(
        max_length=999, null=True, verbose_name="Client Picture/Avatar"
    )
    date_added = models.DateTimeField(default=timezone.now)

    def long(self):
        return {
            "id": self.id,
            "client_id": self._id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "state": self.state,
            "avatar": self.avatar,
        }

    def __str__(self):
        return json.dumps(self.long())


class Gallery(models.Model):
    class Meta:
        db_table = "Gallaries_Table"

    sp_id = models.TextField(verbose_name="SP ID", max_length=20)
    url = models.TextField(max_length=500, verbose_name="Gallery Item URL")
    date_added = models.DateTimeField(default=timezone.now)

    def long(self):
        return {
            "id": self.id,
            "sp_id": self.sp_id,
            "url": self.url,
        }

    def __str__(self):
        return json.dumps(self.long())


class Review(models.Model):
    class Meta:
        db_table = "Reviews_Table"

    sp_id = models.TextField(verbose_name="SP ID", max_length=20)
    client_id = models.TextField(verbose_name="Client ID", max_length=20)
    comment = models.TextField(max_length=999, verbose_name="Review Comment")
    date_added = models.DateTimeField(default=timezone.now)

    def long(self):
        return {
            "id": self.id,
            "sp_id": self.sp_id,
            "client_id": self.client_id,
            "comment": self.comment,
        }

    def __str__(self):
        return json.dumps(self.long())


# Service IDS
# Hair Stylist - 6  (Normal)
# Barber - 2  (Normal)
# Make-up Artist - 3  (Normal)
class Sub_Service(models.Model):
    class Meta:
        db_table = "Sub_Services_Table"

    main_service_id = models.TextField(
        verbose_name="Main Service ID", max_length=20, blank=True
    )
    name = models.TextField(max_length=500, verbose_name="Sub_Service name", blank=True)
    price = models.TextField(max_length=999, verbose_name="Amount", blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    def long(self):
        return {
            "id": self.id,
            "main_service_id": self.main_service_id,
            "name": self.name,
            "amount": self.price,
        }

    def __str__(self):
        return json.dumps(self.long())


class Service(models.Model):
    class Meta:
        db_table = "Services_Table"

    service_name = models.TextField(verbose_name="Service Name", max_length=20)
    type = models.TextField(
        max_length=999, verbose_name="Type of Service (Norma/Special"
    )
    service_avatar = models.TextField(
        max_length=500, verbose_name="Service Avatar", blank=True
    )
    date_added = models.DateTimeField(default=timezone.now)

    def long(self):
        return {
            "id": self.id,
            "service": self.service_name,
            "serviceType": self.type,
            "imgUrl": self.service_avatar,
            "subService": format_data(
                Sub_Service.objects.filter(main_service_id=self.id)
            ),
        }

    def __str__(self):
        return json.dumps(self.long())


class Provider_Services_Rendered(models.Model):
    class Meta:
        db_table = "SP_Services_Table"

    sp_id = models.TextField(verbose_name="Service Provider ID", max_length=20)
    service = models.TextField(max_length=999, verbose_name="Service")
    date_added = models.DateTimeField(default=timezone.now)

    def long(self):
        return {
            "id": self.id,
            "service": self.service_name,
            "sp_id": self.sp_id,
        }

    def __str__(self):
        return json.dumps(self.long())


class Service_Provider(models.Model):
    class Meta:
        db_table = "Service_Providers_table"

    _id = models.CharField(max_length=50, unique=True)
    firstname = models.CharField(max_length=30, verbose_name="Firstname", blank=True)
    lastname = models.CharField(max_length=30, verbose_name="Lastname", blank=True)
    email = models.EmailField(max_length=90, unique=True, verbose_name="Email")
    phone = models.CharField(
        max_length=15, unique=True, null=True, verbose_name="Telephone number"
    )
    password = models.TextField(max_length=200, verbose_name="Password")
    address = models.TextField(max_length=200, verbose_name="Address", null=True)
    state = models.TextField(max_length=200, verbose_name="State", null=True)
    avatar = models.CharField(
        max_length=999, null=True, verbose_name="SP Picture/Avatar"
    )
    longitude = models.TextField(
        max_length=200, verbose_name=" SP Longitude", default="3.3347114"
    )
    latitude = models.TextField(
        max_length=200, verbose_name="SP Latitude", default="6.5089405"
    )
    ratings = models.FloatField(max_length=200, verbose_name="Job Ratings", default=1.0)
    pitch = models.CharField(max_length=999, null=True, verbose_name="Pitch")
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, null=True)
    reviews = models.ForeignKey(
        Review,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Services Rendered",
    )
    # services_rendered = ArrayField(
    #     models.CharField(max_length=1000), blank=True, null=True
    # )
    date_added = models.DateTimeField(default=timezone.now)

    def short(self):
        return {
            "id": self.id,
            "client_id": self._id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "state": self.state,
            "avatar": self.avatar,
        }

    def long(self):
        return {
            "id": self.id,
            "client_id": self._id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "state": self.state,
            "avatar": self.avatar,
            "ratings": self.ratings,
            "pitch": self.pitch,
            # "services_rendered": format_data(self.services_rendered),
            # "gallery": json.loads(self.gallery),
            # "reviews": json.loads(self.reviews),
            "services_rendered": format_data(
                Provider_Services_Rendered.objects.filter(sp_id=self._id).values(
                    "service"
                )
            ),
            # "services_rendered": json.loads(self.services_rendered),
        }

    def longer(self, long, lat):
        return {
            "id": self.id,
            "client_id": self._id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "state": self.state,
            "avatar": self.avatar,
            "ratings": self.ratings,
            "pitch": self.pitch,
            # "services_rendered": format_data(self.services_rendered),
            "distance": distance.distance(
                long, lat, float(self.longitude), float(self.latitude)
            ),
            # "gallery": json.loads(self.gallery),
            # "reviews": json.loads(self.reviews),
            # "services_rendered": format_data(
            #     Provider_Services_Rendered.objects.filter(sp_id=self._id).values(
            #         "service"
            #     )
            # ),
            # "services_rendered": json.loads(self.services_rendered),
        }

    def __str__(self):
        return json.dumps(self.short())
