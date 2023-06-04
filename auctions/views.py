from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms 
from django.utils.translation import gettext_lazy as _

from .models import User, Listing


def index(request):
    return render(request, "auctions/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'image_url', 'category']
        widgets = {
            'description': forms.Textarea()
        }
        labels = {
            'image_url': _('Image URL') 
        }
def add_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user = request.user
    if request.method == 'POST':
        listing = Listing(owner=user)
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid:
            form.save() 
        else:
            return render(request, 'auctions/add_listing.html', {
                'form': form
            })
    return render(request, 'auctions/add_listing.html', {
        'form': ListingForm() 
    })