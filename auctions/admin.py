from django.contrib import admin

from .models import User, Listing, Bid, Comment
# Register your models here.

admin.site.register([User, Listing, Bid, Comment])