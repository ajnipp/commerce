from django.contrib import admin

from .models import User, Listing
# Register your models here.

admin.site.register([User, Listing])