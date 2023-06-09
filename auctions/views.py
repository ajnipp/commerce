from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest 
from django.shortcuts import render
from django.urls import reverse
from django import forms 
from django.utils.translation import gettext_lazy as _

from .models import User, Listing, Bid


def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        'active_listings': active_listings
    })


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

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid 
        fields = ['amount']
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data['amount']
        print(amount)
        if amount <= self.instance.listing.price:
            print("value too small")
            self.add_error('amount', "Bid must be higher than the current price!")

def listing(request, listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    if listing is None:
        return Http404('Listing not found!') 
    if user.is_authenticated:
        is_watching = listing in user.watchlist.all()
    else:
        is_watching = False
    bids = listing.bids.all()
    bid_count = bids.count()
    highest_bid = bids.order_by('-amount').first() 
    if highest_bid is None:
        is_highest_bidder = False
    else:
        is_highest_bidder = highest_bid.bidder == user
    if request.method == 'POST':
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse('login'))
        if user == listing.owner:
            return HttpResponse('Cannot post bid as the owner!') 
        bid = Bid(listing=listing, bidder=user)
        form = BidForm(request.POST, instance=bid) 
        if form.is_valid():
            form.save()
            listing.price = form.cleaned_data['amount']
            listing.save(update_fields=['price'])
        else:
            return render(request, 'auctions/listing.html', {
                'user': user,
                'listing': listing,
                'is_watching': is_watching,
                'bid_count': bid_count,
                'is_highest_bidder': is_highest_bidder,
                'form': form
            })
    return render(request, 'auctions/listing.html', {
        'user': user,
        'listing': listing,
        'is_watching': is_watching,
        'bid_count': bid_count,
        'is_highest_bidder': is_highest_bidder,
        'form': BidForm()
    })

def categories(request):
    pass

def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user = request.user
    return render(request, 'auctions/watchlist.html',{
        'user': user,
        'watchlist': user.watchlist.all()
    })
def watchlist_add(request, listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    if listing is None:
        return Http404(f"Coudn't find listing with id of {listing_id}")
    user.watchlist.add(listing) 
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))

def watchlist_remove(request, listing_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    if listing is None:
        return Http404(f"Coudn't find listing with id of {listing_id}")
    user.watchlist.remove(listing) 
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))