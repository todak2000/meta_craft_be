from django.contrib import admin
from .models import (
    Client,
    Otp,
    Service,
    Service_Provider,
    Sub_Service,
    Review,
    Gallery,
    Provider_Services_Rendered,
    Service_Request,
    Reviews,
)

# Register your models here.
admin.site.register(Client)
admin.site.register(Otp)
admin.site.register(Service)
admin.site.register(Service_Provider)
admin.site.register(Sub_Service)
admin.site.register(Review)
admin.site.register(Gallery)
admin.site.register(Provider_Services_Rendered)
admin.site.register(Service_Request)
admin.site.register(Reviews)
